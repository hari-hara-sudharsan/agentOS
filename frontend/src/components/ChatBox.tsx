import React from "react";

export default function ChatBox() {
    return (
        <div className="w-full max-w-3xl flex-1 bg-gray-800 rounded-t-lg shadow-lg mt-4 flex flex-col p-4 border border-gray-700">
            <div className="flex-1 overflow-y-auto mb-4">
                <p className="text-gray-400 text-center mt-10">No messages yet. Start a conversation!</p>
            </div>
        </div>
    );
}
