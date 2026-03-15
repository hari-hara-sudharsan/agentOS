export async function apiRequest(
  url: string,
  token: string,
  method="GET",
  body?: any
){

  const response = await fetch(url,{
    method,
    headers:{
      "Content-Type":"application/json",
      "Authorization":`Bearer ${token}`
    },
    body: body ? JSON.stringify(body) : undefined
  })

  return response.json()

}
