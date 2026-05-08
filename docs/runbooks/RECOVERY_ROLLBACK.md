# Recovery and Rollback Runbook

1. Pause workers through API: `POST /system/pause`
2. Inspect failed task result.
3. Use patch transaction rollback if a patch was applied.
4. Restore `.serviter` backup if database state is corrupted.
5. Resume workers with `POST /system/resume`.
