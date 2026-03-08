"use client"

export default function ExecutionPanel({goal,steps}:any){

  return(

    <div className="bg-gray-800 p-4 rounded-lg mb-4">

      <h2 className="text-lg mb-3 font-semibold">
        {goal || "Execution"}
      </h2>

      <div className="space-y-2">

        {steps.map((step:any,i:number)=>{

          let icon="⏳"

          if(step.status==="completed") icon="✓"
          if(step.status==="failed") icon="✗"

          return(
            <div
              key={i}
              className="flex justify-between bg-gray-700 px-3 py-2 rounded"
            >

              <span>⚙ {step.tool}</span>

              <span>{icon}</span>

            </div>
          )
        })}

      </div>

    </div>
  )
}