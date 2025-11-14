export async function GET() {
  return Response.json({ 
    message: 'Simple API test working',
    timestamp: new Date().toISOString()
  })
}
