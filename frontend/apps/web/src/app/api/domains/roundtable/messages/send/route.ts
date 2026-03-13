import { getAuth } from '@/core/auth';
import { envConfigs } from '@/config';

export async function POST(request: Request) {
  try {
    const auth = await getAuth();
    const session = await auth.api.getSession({ headers: request.headers });

    if (!session) {
      return Response.json(
        { code: 1, message: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { sessionId, content, generateAiReply = true } = await request.json();

    if (!sessionId || !content) {
      return Response.json(
        { code: 1, message: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Call Python backend
    const backendUrl = envConfigs.python_backend_url || 'http://localhost:8000';
    const response = await fetch(
      `${backendUrl}/api/v1/roundtable/sessions/${sessionId}/messages`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Pass session token from cookies
          Cookie: request.headers.get('Cookie') || '',
        },
        body: JSON.stringify({
          content,
          generate_ai_reply: generateAiReply,
        }),
      }
    );

    const data = await response.json();

    // Handle error responses from backend
    if (!response.ok) {
      return Response.json(
        {
          code: data.code || 1,
          message: data.message || 'Failed to send message',
        },
        { status: response.status }
      );
    }

    // Return success response
    return Response.json({
      code: 0,
      data: {
        userMessage: data.data?.userMessage,
        aiReplies: data.data?.aiReplies || [],
        status: data.data?.status || 'success',
        sessionId,
      },
    });
  } catch (error: any) {
    console.error('Error sending message:', error);
    return Response.json(
      { code: 1, message: 'Internal server error' },
      { status: 500 }
    );
  }
}
