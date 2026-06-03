# Log Diagnosis Report

## Summary

Docker failed to start because the requested host port is already in use.

## Detected Pattern

- Docker port conflict
- Confidence: 0.99
- Risk: medium

## Likely Causes

- A host web server is already listening on the port.
- Another container is using the same host port.
- A previous service did not stop cleanly.

## Checklist

1. Check which process owns the port.
   `sudo lsof -i :80`
   Risk: low
2. Check running containers.
   `docker ps`
   Risk: low
3. Change the container port mapping if needed.
   `docker run -p 8080:80 image-name`
   Risk: low

## Commands

- `sudo lsof -i :80`
- `docker ps`
- `docker run -p 8080:80 image-name`

## Risk Notes

- Do not stop a production host service before identifying what owns the port.
