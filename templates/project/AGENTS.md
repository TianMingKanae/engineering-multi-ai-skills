# Engineering agent agreement

Follow the user's task and this project's existing instructions. Read context/CURRENT_WORK.md and the specific thread assigned to your role; consult FACTS.md only for relevant environment facts. Re-check facts likely to have changed.

Use the responsibilities the task needs: O coordinates and integrates, P proposes, I implements, C reviews, V independently verifies, W executes bounded commands. These role names do not choose a model or authorize delegation. The coordinator records owned files and integration strategy before concurrent writes.

Keep one current owner in each discussion thread's frontmatter. Append a `### ROLE <timestamp>` entry with evidence read, work performed, exact revision/commands/output paths, limits and next action. Update the frontmatter owner on handoff; close or resolve finished work. Do not rewrite other agents' entries.

Use an isolated clone or worktree when other sessions write concurrently. Never pull or replace code underneath a running job. Stage only intended files; use the project's established review/integration flow. Dispatchers do not commit or push for you.

Inspect produced artifacts before claiming completion. Return reproducible failures to the owner; make only fixes within your assigned scope. An independent verifier must not be the result's author. Use context/CLAIMS.md for important conclusions and context/LESSONS.md for supported process lessons. A review may validly recommend no change.

Finish bounded tasks and exit. Do not run idle model calls or create background automation unless authorized. Do not change credentials, permissions or sandbox settings as a side effect of adopting this agreement.
