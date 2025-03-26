# AWS Deployment Guide

This guide will help you deploy the URL Shortener application on AWS using EC2, RDS, and Route 53.

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI installed and configured
3. Domain name registered (for Route 53)
4. SSH key pair for EC2 instance

## Step 1: Set Up RDS (PostgreSQL)

1. Go to RDS in AWS Console
2. Click "Create database"
3. Choose PostgreSQL
4. Select appropriate settings:
   - Dev/Test or Production
   - DB instance class (e.g., db.t3.micro for development)
   - Multi-AZ deployment (recommended for production)
   - Storage type and size
5. Configure:
   - DB instance identifier
   - Master username
   - Master password
6. Advanced settings:
   - VPC settings
   - Security group
   - Initial database name
7. Note down the endpoint, port, database name, username, and password

## Step 2: Launch EC2 Instance

1. Go to EC2 in AWS Console
2. Launch new instance:
   - Choose Ubuntu Server 20.04 LTS
   - Select instance type (e.g., t2.micro)
   - Configure instance details
   - Add storage (default is usually sufficient)
   - Configure security group:
     ```
     - SSH (Port 22) from your IP
     - HTTP (Port 80) from anywhere
     - HTTPS (Port 443) from anywhere
     ```
3. Launch instance with your key pair

## Step 3: Configure Domain with Route 53

1. Create hosted zone in Route 53
2. Add domain records:
   ```
   Type: A
   Name: yourdomain.com
   Value: EC2 instance IP
   ```
3. Update name servers at your domain registrar

## Step 4: Set Up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## Step 5: Deploy Application

1. SSH into EC2 instance:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv nginx
   ```

3. Clone repository:
   ```bash
   git clone your-repo-url
   cd url-shortener
   ```

4. Set up Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. Create .env file:
   ```bash
   echo "DATABASE_URL=postgresql://user:password@your-rds-endpoint:5432/dbname
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30" > .env
   ```

6. Set up Gunicorn service:
   ```bash
   sudo nano /etc/systemd/system/urlshortener.service
   ```
   Add:
   ```ini
   [Unit]
   Description=URL Shortener
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/url-shortener
   Environment="PATH=/home/ubuntu/url-shortener/venv/bin"
   ExecStart=/home/ubuntu/url-shortener/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

   [Install]
   WantedBy=multi-user.target
   ```

7. Configure Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/urlshortener
   ```
   Add:
   ```nginx
   server {
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

8. Enable and start services:
   ```bash
   sudo ln -s /etc/nginx/sites-available/urlshortener /etc/nginx/sites-enabled/
   sudo systemctl start urlshortener
   sudo systemctl enable urlshortener
   sudo systemctl restart nginx
   ```

## Monitoring and Maintenance

1. Set up CloudWatch for monitoring:
   - CPU utilization
   - Memory usage
   - Disk I/O
   - Network traffic

2. Configure backup for RDS:
   - Automated backups
   - Snapshot schedule

3. Set up alerts for:
   - High resource usage
   - Error rates
   - Database connection issues

## Security Considerations

1. Keep security groups restricted
2. Regularly update system packages
3. Monitor AWS CloudTrail logs
4. Use AWS WAF for additional security
5. Implement rate limiting
6. Regular security audits

## Scaling

1. Use Auto Scaling groups for EC2
2. Consider using Elastic Load Balancer
3. Implement caching with Redis/ElastiCache
4. Use CloudFront for static content
5. Monitor and adjust RDS instance class as needed

## Troubleshooting

1. Check application logs:
   ```bash
   sudo journalctl -u urlshortener
   ```

2. Check Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Monitor RDS logs in CloudWatch

4. Common issues:
   - Database connection errors
   - SSL certificate renewal
   - Resource constraints
   - DNS propagation 