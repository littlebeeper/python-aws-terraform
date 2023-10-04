Our current stack is composed of the following components:

- Fargate ECS cluster for serving our API (fully in terraform)
- Networking to make the above possible (fully in terraform)
- MongoDB Atlas for our database (fully in terraform)
- S3 / Cloudfront for serving our static website assets (not in terraform yet)
- S3 / Cloudfront for serving video assets (not in terraform yet)
- AWS CloudFormation rube goldberg machine for transcoding video (not in terraform yet)

This terraform module represents that stack for both qa and production. We use 
terraform workspaces to manage the differences between the two environments.
