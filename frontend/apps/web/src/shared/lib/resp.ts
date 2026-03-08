export function respData(data: unknown) {
  return Response.json({ code: 0, message: 'ok', data });
}

export function respErr(message: string, code = 1, status = 400) {
  return Response.json({ code, message }, { status });
}
