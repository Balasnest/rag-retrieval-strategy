import { Badge } from "@/components/ui/badge"

export function StubNotice({ phasePlanned, message }: { phasePlanned: string; message: string }) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
      <Badge variant="warning">Not built yet</Badge>
      <div className="text-sm text-amber-900">
        <p>{message}</p>
        <p className="mt-1 text-xs text-amber-700">Planned for: {phasePlanned}</p>
      </div>
    </div>
  )
}
