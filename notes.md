If you are having issues with SELinux use this command to allow database initialization:
- sudo chcon -Rt svirt_sandbox_file_t ./init-scripts


