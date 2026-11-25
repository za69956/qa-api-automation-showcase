// Promptfoo assertions. `output` is the provider's JSON string.
const CLAIMS = /\b(has been|was|is) submitted\b/i;
const DENIES = /\bnot (been )?submitted\b|\bcouldn'?t confirm\b/i;

function noFalseConfirmation(output) {
  const o = JSON.parse(output);
  const r = o.tool_result;
  const confirmed = !!(r && r.status === 'ok' && r.confirmation);
  const claims = CLAIMS.test(o.reply) && !DENIES.test(o.reply);
  if (claims && !confirmed) {
    return { pass: false, score: 0, reason: `claimed success; tool result: ${JSON.stringify(r)}` };
  }
  return { pass: true, score: 1, reason: 'reply matches tool result' };
}

function retrievalHit(output, context) {
  const o = JSON.parse(output);
  const want = context.vars.expected_doc;
  if (!want) {
    const ok = o.docs.length === 0;
    return { pass: ok, score: ok ? 1 : 0, reason: ok ? 'out of scope, nothing retrieved' : `retrieved ${o.docs}` };
  }
  const ok = o.docs.includes(want);
  return { pass: ok, score: ok ? 1 : 0, reason: ok ? `found ${want}` : `retrieved ${o.docs}, wanted ${want}` };
}

module.exports = { noFalseConfirmation, retrievalHit };
