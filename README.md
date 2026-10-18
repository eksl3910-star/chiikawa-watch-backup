# Website backup publisher

This repository contains only the code for publishing backup media assets for
the Chiikawa Watch website. It is not a public download service.

Video files, website source code, credentials and account tokens are not committed.
The integration test downloads one sample video into temporary runner storage,
verifies that an MP4 was produced, and deletes it before the job exits.

The active publisher uses Cloudflare in Seoul to stage the original video and
audio in private R2 storage. Standard GitHub-hosted Ubuntu runners merge the
staged tracks with FFmpeg without re-encoding, verify the result, and upload it
through a dedicated authenticated publisher API. GitHub never needs to download
directly from YouTube. Only missing episodes from the verified website catalog
are processed. No personal computer or self-hosted runner is required.

Publication checks run on Thursdays and Fridays at 11:17, 13:17 and 15:17 Korea
time (02:17, 04:17 and 06:17 UTC). GitHub may delay scheduled runs. Manual probe
mode tests the complete pipeline using a temporary object and preserves the
existing episode backup. A 1080p end-to-end probe succeeded on 2026-10-18.

The `BACKUP_TOKEN` repository secret is limited to the backup publisher API;
Cloudflare account credentials are not stored here. Temporary R2 staging and
probe objects are deleted after success and expire after one day if abandoned.
The actual health report is committed after runs, providing an auditable record
of checks and keeping this scheduled repository active. A failed check is
reported as a failure instead of claiming successful backups.

The public standard runner is free. R2 storage and operations must stay within
the account's monthly allowance. The publisher stops at its own 8GB budget;
this does not limit unrelated projects in the same Cloudflare account.

Use only with content you have permission to download and publish.
