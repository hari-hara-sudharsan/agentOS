"use client"

import { useEffect,useState } from "react"
import IntegrationCard from "../../components/IntegrationCard"

export default function Integrations(){

  const [services,setServices]=useState([])

  useEffect(()=>{

    fetch("http://localhost:8000/api/integrations")
      .then(r=>r.json())
      .then(setServices)

  },[])

  return(

    <div>

      <h2 className="text-xl font-bold mb-4">
        Connected Services
      </h2>

      <div className="grid grid-cols-2 gap-4">

        {services.map((s:any)=>(
          <IntegrationCard key={s.service} service={s}/>
        ))}

      </div>

    </div>

  )

}
