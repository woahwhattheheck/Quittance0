"""Apply the four reviewed merge resolutions; no publication or provider calls."""
from pathlib import Path
import re
import subprocess

root = Path.cwd()
up = '282c75ad933651a93b89a8412ab649b48714c739'
expected = {
    'backend/src/routes/invoice.handlers.ts',
    'backend/src/services/invoice-memory.service.ts',
    'backend/src/services/invoice.service.ts',
    'backend/tests/invoice-cancel-payment-race.test.ts',
}
conflicts = set(subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=U'], text=True).splitlines())
if conflicts != expected:
    raise SystemExit(f'Unexpected merge conflicts: {sorted(conflicts)}')

def resolve(path, transform):
    p = root / path
    n = 0
    def replace(match):
        nonlocal n
        n += 1
        return transform(match[1], match[2])
    text = re.sub(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> ' + up + r'\n', replace, p.read_text(), flags=re.S)
    if n != 1:
        raise SystemExit(f'Unexpected conflict count for {path}: {n}')
    p.write_text(text)

resolve('backend/src/routes/invoice.handlers.ts', lambda ours, theirs: ours.replace("        logError('Cancel invoice error:', error);\n", '') + theirs)
resolve('backend/src/services/invoice-memory.service.ts', lambda ours, theirs: theirs[:theirs.index("    if (existing.status !== 'PENDING')")] + ours)
resolve('backend/src/services/invoice.service.ts', lambda ours, theirs: "        throw new Error('Invoice not found');\n")
resolve('backend/tests/invoice-cancel-payment-race.test.ts', lambda ours, theirs: ours)
p = root / 'backend/tests/invoice-state-machine.test.ts'
s = p.read_text()
s = s.replace("import { createInvoiceHandlers }", "import { InvoiceTerminalConflictError } from '../src/domain/invoice-settlement.ts';\nimport { createInvoiceHandlers }")
s = s.replace('cancelInvoice returns 400 with INVOICE_ALREADY_PAID', 'cancelInvoice returns 409 with INVOICE_ALREADY_PAID').replace('cancelInvoice returns 400 with INVOICE_NOT_PENDING', 'cancelInvoice returns 409 with INVOICE_ALREADY_CANCELLED').replace('cancelInvoice returns 400 with INVOICE_EXPIRED', 'cancelInvoice returns 409 with INVOICE_EXPIRED')
s = s.replace('assert.equal(cancelRes.statusCode, 400);', 'assert.equal(cancelRes.statusCode, 409);').replace('assert.equal(secondCancelRes.statusCode, 400);', 'assert.equal(secondCancelRes.statusCode, 409);').replace("assert.equal(secondCancelRes.body.code, 'INVOICE_NOT_PENDING');", "assert.equal(secondCancelRes.body.code, 'INVOICE_ALREADY_CANCELLED');\n    assert.equal(secondCancelRes.body.status, 'CANCELLED');")
old = "() => storage.cancelInvoice(paid.id, SELLER_KEY),\n      (err: any) => {\n        assert.equal(err instanceof IllegalStateTransitionError, true);"
if old not in s:
    raise SystemExit('Storage cancellation assertion not found')
s = s.replace(old, old.replace('IllegalStateTransitionError', 'InvoiceTerminalConflictError'))
s = s.replace("assert.equal(cancelRes.body.code, 'INVOICE_ALREADY_PAID');", "assert.equal(cancelRes.body.code, 'INVOICE_ALREADY_PAID');\n    assert.equal(cancelRes.body.status, 'PAID');\n    assert.equal(cancelRes.body.paymentTxHash, 'a'.repeat(64));")
s = s.replace("assert.equal(cancelRes.body.code, 'INVOICE_EXPIRED');", "assert.equal(cancelRes.body.code, 'INVOICE_EXPIRED');\n    assert.equal(cancelRes.body.status, 'EXPIRED');")
p.write_text(s)
subprocess.run(['git', 'add', *sorted(expected), str(p.relative_to(root))], check=True)
tree = subprocess.check_output(['git', 'write-tree'], text=True).strip()
if tree != '4edbd31b3357dda6ebd7a1d901f51f19b5ff252d':
    raise SystemExit(f'Resolved tree differs from locally reviewed candidate: {tree}')
print(tree)
