import { defineTool } from '@deepseek-ai/dsh-tools';
import { inspectEntity } from './domain.js';

export const inject = ['tools'];

/** Register a read-only example. No persistent data or external I/O is used. */
export function apply(ctx) {
  ctx.tools.register(defineTool({
    name: '__TOOL__',
    description: 'Inspect the synthetic example entity example:equipment-1. This is not a live ontology database.',
    parameters: { id: { type: 'string', required: true, description: 'Entity identifier' } },
    output: {
      schema: {
        type: 'object', additionalProperties: false,
        properties: {
          status: { type: 'string', required: true },
          id: { type: 'string', required: true },
          label: { type: 'string', required: true },
          entityType: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    execute(args, exec) {
      exec.signal.throwIfAborted();
      return inspectEntity(args.id);
    },
  }));
}
