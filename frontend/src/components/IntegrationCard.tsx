"use client"

export default function IntegrationCard({service}:any){

  const connect=()=>{

    alert(`Connect ${service.service}`)

  }

  return(

    <div className="bg-white p-4 rounded shadow">

      <h3 className="font-bold">
        {service.service}
      </h3>

      <p className="text-sm mb-2">

        {service.connected
          ? "Connected"
          : "Not Connected"}

      </p>

      {!service.connected &&(

        <button
          onClick={connect}
          className="bg-blue-500 text-white px-3 py-1 rounded"
        >
          Connect
        </button>

      )}

    </div>

  )

}
