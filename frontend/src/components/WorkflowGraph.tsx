"use client"

import ReactFlow from "reactflow"
import "reactflow/dist/style.css"

export default function WorkflowGraph({steps}:any){

  const nodes = steps.map((s:any,i:number)=>({
    id:String(i),
    data:{label:s.tool},
    position:{x:i*200,y:50}
  }))

  const edges = steps.slice(1).map((_:any,i:number)=>({
    id:`e${i}`,
    source:String(i),
    target:String(i+1)
  }))

  return(

    <div style={{height:200}}>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      />

    </div>

  )

}
