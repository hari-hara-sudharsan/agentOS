"use client"

import { useEffect,useState } from "react"

export default function Activity(){

  const [data,setData]=useState([])

  useEffect(()=>{

    fetch("http://localhost:8000/api/activity/analytics")
      .then(r=>r.json())
      .then(setData)

  },[])

  return(

    <div>

      <h2 className="text-xl font-bold mb-4">
        Agent Activity
      </h2>

      <table className="w-full bg-white rounded shadow">

        <thead>

          <tr>

            <th>Task</th>
            <th>Status</th>
            <th>Execution Time</th>

          </tr>

        </thead>

        <tbody>

          {data.map((d:any,i)=>(
            <tr key={i}>

              <td>{d.task_name}</td>
              <td>{d.status}</td>
              <td>{d.execution_time}s</td>

            </tr>
          ))}

        </tbody>

      </table>

    </div>

  )

}
