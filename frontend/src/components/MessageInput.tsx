export default function StepList({steps}:any) {

  return (
    <div className="space-y-2 mb-4">

      {steps.map((step:any,i:number)=>(

        <div key={i} className="text-sm">

          {step.status === "completed" ? "✓" : "⏳"} {step.tool}

        </div>

      ))}

    </div>
  )
}