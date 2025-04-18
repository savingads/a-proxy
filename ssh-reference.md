# SSH Command Reference for Digital Ocean Deployment

This document provides reference commands for accessing your Digital Ocean droplet at 209.38.62.85 using the existing SSH key.

## Key Location

The SSH key is located at:
```
~/.ssh/do_temp_key
```

## SSH Connection

To connect to the Digital Ocean droplet:

```bash
ssh -i ~/.ssh/do_temp_key chris@209.38.62.85
```

## SCP File Transfer

To copy the deployment script to the server:

```bash
scp -i ~/.ssh/do_temp_key deploy.sh chris@209.38.62.85:~/
```

To copy multiple files:

```bash
scp -i ~/.ssh/do_temp_key deploy.sh merge-to-main.sh DEPLOYMENT.md chris@209.38.62.85:~/
```

## Deployment Steps Using the Key

1. Copy the deployment script to the server:
   ```bash
   scp -i ~/.ssh/do_temp_key deploy.sh chris@209.38.62.85:~/
   ```

2. SSH into the server:
   ```bash
   ssh -i ~/.ssh/do_temp_key chris@209.38.62.85
   ```

3. Make the script executable:
   ```bash
   chmod +x ~/deploy.sh
   ```

4. Run the deployment script:
   ```bash
   sudo ~/deploy.sh
   ```

## SSH Config Option (Optional)

To avoid specifying the identity file each time, you can add an entry to your SSH config:

```bash
# Create or edit ~/.ssh/config
cat >> ~/.ssh/config << EOL
Host do-droplet
    HostName 209.38.62.85
    User chris
    IdentityFile ~/.ssh/do_temp_key
    StrictHostKeyChecking no
EOL
```

Then you can simply use:
```bash
ssh do-droplet
scp deploy.sh do-droplet:~/
