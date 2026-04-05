"""
OpenClaw Bridge - Secure connection to local LLM sandbox
Implements Token Vault security for all agent-to-LLM communications
"""
import logging
import time
import httpx
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from utils.metrics import (
    track_openclaw_request, 
    set_openclaw_sessions,
    OPENCLAW_ACTIVE_SESSIONS
)
from security.auth0_client import check_mfa_and_consent

logger = logging.getLogger(__name__)


class OpenClawModel(str, Enum):
    """Supported OpenClaw models"""
    LLAMA3 = "llama3"
    LLAMA3_70B = "llama3:70b"
    MISTRAL = "mistral"
    CODELLAMA = "codellama"
    MIXTRAL = "mixtral"
    PHI3 = "phi3"


@dataclass
class OpenClawConfig:
    """OpenClaw connection configuration"""
    host: str = "localhost"
    port: int = 11434
    timeout: float = 120.0
    default_model: str = "llama3"
    max_retries: int = 3
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class OpenClawBridge:
    """
    Secure bridge between AgentOS and OpenClaw (local LLM sandbox)
    
    All requests are mediated through the Token Vault security layer
    to ensure proper consent and audit logging.
    """
    
    def __init__(self, config: Optional[OpenClawConfig] = None):
        self.config = config or OpenClawConfig()
        self.client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        logger.info(f"OpenClaw bridge initialized: {self.config.base_url}")
    
    def _update_session_count(self):
        """Update Prometheus gauge for active sessions"""
        set_openclaw_sessions(len(self._active_sessions))
    
    def generate(
        self,
        user_context: Dict[str, Any],
        prompt: str,
        model: str = None,
        system: str = None,
        context: List[int] = None,
        stream: bool = False,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate text completion from OpenClaw
        
        Args:
            user_context: Auth0 user context for consent checks
            prompt: The input prompt
            model: Model to use (default from config)
            system: System prompt for context
            context: Previous conversation context (token IDs)
            stream: Whether to stream response
            options: Model parameters (temperature, top_p, etc.)
        
        Returns:
            Generated response with metadata
        """
        # Security check - ensure user has consent for AI operations
        check_mfa_and_consent(
            user_context, 
            {"prompt": prompt[:100]},  # Log truncated prompt
            tool="openclaw_generate"
        )
        
        model = model or self.config.default_model
        start_time = time.time()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        if context:
            payload["context"] = context
        if options:
            payload["options"] = options
        
        try:
            response = self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            result = response.json()
            
            duration = time.time() - start_time
            track_openclaw_request("generate", "success", duration)
            
            logger.info(f"OpenClaw generate: model={model}, duration={duration:.2f}s")
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "model": model,
                "context": result.get("context"),
                "total_duration": result.get("total_duration"),
                "eval_count": result.get("eval_count"),
                "tokens_per_second": result.get("eval_count", 0) / duration if duration > 0 else 0
            }
            
        except httpx.HTTPStatusError as e:
            duration = time.time() - start_time
            track_openclaw_request("generate", "failure", duration)
            logger.error(f"OpenClaw HTTP error: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            duration = time.time() - start_time
            track_openclaw_request("generate", "failure", duration)
            logger.error(f"OpenClaw error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def chat(
        self,
        user_context: Dict[str, Any],
        messages: List[Dict[str, str]],
        model: str = None,
        stream: bool = False,
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Chat completion with message history
        
        Args:
            user_context: Auth0 user context
            messages: List of messages [{"role": "user/assistant", "content": "..."}]
            model: Model to use
            stream: Whether to stream response
            options: Model parameters
        
        Returns:
            Chat response with message
        """
        check_mfa_and_consent(
            user_context,
            {"message_count": len(messages)},
            tool="openclaw_chat"
        )
        
        model = model or self.config.default_model
        start_time = time.time()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream
        }
        
        if options:
            payload["options"] = options
        
        try:
            response = self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            
            duration = time.time() - start_time
            track_openclaw_request("chat", "success", duration)
            
            return {
                "success": True,
                "message": result.get("message", {}),
                "model": model,
                "total_duration": result.get("total_duration"),
                "eval_count": result.get("eval_count")
            }
            
        except Exception as e:
            duration = time.time() - start_time
            track_openclaw_request("chat", "failure", duration)
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_embedding(
        self,
        user_context: Dict[str, Any],
        text: str,
        model: str = "nomic-embed-text"
    ) -> Dict[str, Any]:
        """
        Create text embeddings for RAG/semantic search
        
        Args:
            user_context: Auth0 user context
            text: Text to embed
            model: Embedding model
        
        Returns:
            Embedding vector
        """
        check_mfa_and_consent(
            user_context,
            {"text_length": len(text)},
            tool="openclaw_embedding"
        )
        
        start_time = time.time()
        
        try:
            response = self.client.post("/api/embeddings", json={
                "model": model,
                "prompt": text
            })
            response.raise_for_status()
            result = response.json()
            
            duration = time.time() - start_time
            track_openclaw_request("embedding", "success", duration)
            
            return {
                "success": True,
                "embedding": result.get("embedding", []),
                "model": model
            }
            
        except Exception as e:
            duration = time.time() - start_time
            track_openclaw_request("embedding", "failure", duration)
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_models(self) -> Dict[str, Any]:
        """List available models on OpenClaw"""
        start_time = time.time()
        
        try:
            response = self.client.get("/api/tags")
            response.raise_for_status()
            result = response.json()
            
            duration = time.time() - start_time
            track_openclaw_request("list_models", "success", duration)
            
            models = [
                {
                    "name": m.get("name"),
                    "size": m.get("size"),
                    "modified": m.get("modified_at")
                }
                for m in result.get("models", [])
            ]
            
            return {
                "success": True,
                "models": models
            }
            
        except Exception as e:
            duration = time.time() - start_time
            track_openclaw_request("list_models", "failure", duration)
            return {
                "success": False,
                "error": str(e)
            }
    
    def pull_model(
        self,
        user_context: Dict[str, Any],
        model: str
    ) -> Dict[str, Any]:
        """
        Pull/download a model to OpenClaw
        
        Requires elevated consent due to resource usage
        """
        # High-stakes action - explicit consent required
        check_mfa_and_consent(
            user_context,
            {"model": model},
            tool="openclaw_pull_model"
        )
        
        start_time = time.time()
        
        try:
            response = self.client.post("/api/pull", json={
                "name": model,
                "stream": False
            })
            response.raise_for_status()
            
            duration = time.time() - start_time
            track_openclaw_request("pull_model", "success", duration)
            
            return {
                "success": True,
                "model": model,
                "message": f"Model {model} pulled successfully"
            }
            
        except Exception as e:
            duration = time.time() - start_time
            track_openclaw_request("pull_model", "failure", duration)
            return {
                "success": False,
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check OpenClaw service health"""
        try:
            response = self.client.get("/")
            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    def create_session(
        self,
        user_context: Dict[str, Any],
        session_id: str,
        model: str = None,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Create a persistent chat session
        
        Sessions maintain conversation context across multiple interactions
        """
        model = model or self.config.default_model
        
        self._active_sessions[session_id] = {
            "user_id": user_context.get("sub"),
            "model": model,
            "system_prompt": system_prompt,
            "messages": [],
            "context": None,
            "created_at": time.time()
        }
        
        self._update_session_count()
        
        logger.info(f"OpenClaw session created: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "model": model
        }
    
    def session_chat(
        self,
        user_context: Dict[str, Any],
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Chat within an existing session (maintains context)
        """
        if session_id not in self._active_sessions:
            return {
                "success": False,
                "error": f"Session {session_id} not found"
            }
        
        session = self._active_sessions[session_id]
        
        # Verify user owns this session
        if session["user_id"] != user_context.get("sub"):
            return {
                "success": False,
                "error": "Session does not belong to user"
            }
        
        # Add user message to history
        session["messages"].append({
            "role": "user",
            "content": message
        })
        
        # Prepare messages for API
        messages = []
        if session.get("system_prompt"):
            messages.append({
                "role": "system",
                "content": session["system_prompt"]
            })
        messages.extend(session["messages"])
        
        # Call chat API
        result = self.chat(
            user_context,
            messages,
            model=session["model"]
        )
        
        if result["success"]:
            # Add assistant response to history
            assistant_message = result["message"]
            session["messages"].append(assistant_message)
        
        return result
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a chat session"""
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
            self._update_session_count()
            
            return {
                "success": True,
                "message": f"Session {session_id} ended"
            }
        
        return {
            "success": False,
            "error": f"Session {session_id} not found"
        }
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.client.close()
        except:
            pass


# Singleton instance
_openclaw_bridge: Optional[OpenClawBridge] = None


def get_openclaw_bridge() -> OpenClawBridge:
    """Get or create OpenClaw bridge singleton"""
    global _openclaw_bridge
    if _openclaw_bridge is None:
        import os
        config = OpenClawConfig(
            host=os.getenv("OPENCLAW_HOST", "localhost"),
            port=int(os.getenv("OPENCLAW_PORT", "11434")),
            default_model=os.getenv("OPENCLAW_MODEL", "llama3")
        )
        _openclaw_bridge = OpenClawBridge(config)
    return _openclaw_bridge


# Tool functions for agent registry
def openclaw_generate(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool: Generate text with OpenClaw"""
    bridge = get_openclaw_bridge()
    return bridge.generate(
        user_context,
        prompt=params.get("prompt", ""),
        model=params.get("model"),
        system=params.get("system"),
        options=params.get("options")
    )


def openclaw_chat(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool: Chat with OpenClaw"""
    bridge = get_openclaw_bridge()
    return bridge.chat(
        user_context,
        messages=params.get("messages", []),
        model=params.get("model"),
        options=params.get("options")
    )


def openclaw_list_models(user_context: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Agent tool: List available OpenClaw models"""
    bridge = get_openclaw_bridge()
    return bridge.list_models()


# Register tools
from registry.tool_registry import tool_registry
tool_registry.register("openclaw_generate", openclaw_generate)
tool_registry.register("openclaw_chat", openclaw_chat)
tool_registry.register("openclaw_list_models", openclaw_list_models)
