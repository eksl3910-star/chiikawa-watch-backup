# Website backup publisher

This repository contains only the code for publishing backup media assets for
the Chiikawa Watch website. It is not a public download service.

Video files, website source code, credentials and account tokens are not committed.
The integration test downloads one sample video into temporary runner storage,
verifies that an MP4 was produced, and deletes it before the job exits.

Scheduled publication will only be enabled after the provider test succeeds.
Use only with content you have permission to download and publish.
