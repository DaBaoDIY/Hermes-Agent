#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-us-east-1}"
CHANGE_SET_ID="${CHANGE_SET_ID:-${1:-}}"

if [[ -z "${CHANGE_SET_ID}" ]]; then
  echo "Usage: CHANGE_SET_ID=<id> $0" >&2
  echo "   or: $0 <id>" >&2
  exit 1
fi

aws marketplace-catalog describe-change-set \
  --catalog AWSMarketplace \
  --change-set-id "${CHANGE_SET_ID}" \
  --region "${REGION}" \
  --query '{
    ChangeSetId:ChangeSetId,
    Status:Status,
    FailureCode:FailureCode,
    FailureDescription:FailureDescription,
    StartTime:StartTime,
    EndTime:EndTime,
    Changes:ChangeSet[].{
      ChangeName:ChangeName,
      ChangeType:ChangeType,
      Entity:Entity,
      Details:Details,
      ErrorDetailList:ErrorDetailList
    }
  }' \
  --output json
