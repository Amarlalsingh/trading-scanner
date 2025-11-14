import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    message: 'Trading Scanner API is running (Next.js)',
    timestamp: new Date().toISOString()
  })
}
