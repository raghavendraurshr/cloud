import psutil
import time
import boto3
import paramiko
import random
import string

# Thresholds
MAX_CPU_THRESHOLD = 65  # in percentage
MAX_MEMORY_THRESHOLD = 100 # in percentage

MIN_CPU_THRESHOLD =  30 # in percentage
MIN_MEMORY_THRESHOLD = 5 # in percentage

def check_system_usage():
    global launched

    cpu_usage = psutil.cpu_percent(interval=1)

    # Get memory usage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
   
    print(f"Current CPU usage: {cpu_usage}%")
    print(f"Current MEMORY usage: {memory_usage}%")
    append_string = f'   server {instance_id} {public_ip_aws_vm}:5004 check'
    if launched == 0 :
        if cpu_usage > MAX_CPU_THRESHOLD or memory_usage > MAX_MEMORY_THRESHOLD:
            launched=1
            print("\nLaunching AWS instance !!")
            create_ec2_instance()
            append_string = f'   server {instance_id} {public_ip_aws_vm}:5004 check'
            #print(append_string)
            ssh_and_modify_file(haproxy_ip, haproxy_username,  file_path, search_string, append_string,False)
    elif launched == 1:
        if memory_usage < MIN_MEMORY_THRESHOLD or cpu_usage < MIN_CPU_THRESHOLD:
            print("\nTerminating AWS instance  !!")
            instance = ec2.Instance(instance_id)
            response = instance.terminate()
            #print(response)
            append_string = f'   server {instance_id} {public_ip_aws_vm}:5004 check'
            ssh_and_modify_file(haproxy_ip, haproxy_username,  file_path, search_string, append_string,True)
            launched = 0


instance_id=0
ec2=None
public_ip_aws_vm=None

def create_ec2_instance():
    global ec2
    global public_ip_aws_vm
    global instance_id

    # Create a session using your AWS credentials and region

    session = boto3.Session(
        aws_access_key_id='AKIA2ZWW2Z2ASK7HMVXT',
        aws_secret_access_key='k4zo5QkuZbTcU4x6Suq7nQt6dwhpKnFAo5J4Sq8c',
        region_name='us-east-2'
    )

    # Use the session to create an EC2 resource
    ec2 = session.resource('ec2')
    instance_name = "AWS-SSE-"+''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 3)))
    tags = [
         {'Key': 'Name', 'Value': instance_name},
          {'Key': 'Hostname', 'Value': f'{instance_name.lower()}-ec2-hostname'}  #not working as of now
          ]

    # Create a new EC2 instance
    instances = ec2.create_instances(
        ImageId='ami-09040d770ffe2224f',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='haproxy',
        SecurityGroupIds=['sg-0340a6cb9f1923c12'],
        SubnetId='subnet-b7df24df',
        TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': tags
        }]
    )

    for instance in instances:
        instance.wait_until_running()
        instance.reload()
        time.sleep(30)
        print(f'Instance {instance.id} created with public IP: {instance.public_ip_address}')
        public_ip_aws_vm=instance.public_ip_address
        #public_ip ='18.116.90.30'
        private_ip_aws_vm=instance.private_ip_address
        key_path = '/root/haproxy.pem'
        username_aws = 'ubuntu'  # Ubuntu AMI default user
        commands = [
    'sudo apt-get update',
    'sudo apt-get install -y python3 python3-pip python3-flask python3-mysql.connector python3-psutil',
     'wget https://raw.githubusercontent.com/raghavendraurshr/cloud/main/cpu.py',
    'mkdir -p cloud && cd cloud && wget https://raw.githubusercontent.com/raghavendraurshr/cloud/main/app.py && mkdir -p templates && cd templates && wget https://raw.githubusercontent.com/raghavendraurshr/cloud/main/templates/index.html',
    'private_ip=$(hostname -I | awk \'{print $1}\') && sed -i "s/PRIVATE-IP/$private_ip/g" /home/ubuntu/cloud/app.py',
    'python3 /home/ubuntu/cloud/app.py > /dev/null 2>&1 &'
]
 
        ec2 = session.resource('ec2')
        instance_id = instance.id
        instance_id=str(instance_id)
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the EC2 instance
        ssh.connect(hostname=public_ip_aws_vm, username=username_aws, key_filename=key_path)

        # Execute commands
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            print(stderr.read().decode())
           # print(stdout.read().decode())
        # Close the SSH connection
        ssh.close()
		


launched = 0

def ssh_and_modify_file(host, username,  file_path, marker, content_to_modify,is_haproxy):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the target machine
        print(f"Connecting to HAPROXY {host}...")
        #password = getpass.getpass(prompt='Enter your SSH password: ')
        password="HP!nvent123"
        ssh.connect(hostname=host, username=username, password=password)
        print(f"Successfully connected to HAPROXY {host}")

        # Read the file content
        sftp = ssh.open_sftp()
        with sftp.open(file_path, 'r') as file:
            file_lines = file.readlines()

        # Append content to the specified part of the file
        if is_haproxy ==False:
            modified_file_lines = append_content(file_lines, marker, content_to_modify)
        else:
            modified_file_lines=delete_content(file_lines,content_to_modify)

        # Write the modified content back to the file
        with sftp.open(file_path, 'w') as file:
            file.writelines(modified_file_lines)

        # Close the SFTP session
        sftp.close()


        stdin, stdout, stderr = ssh.exec_command('sudo service haproxy restart')
        stdout_str = stdout.read().decode()
        stderr_str = stderr.read().decode()


        # Close the SSH connection
        ssh.close()
        print(f"Exiting from HAPROXY {host}")
    except Exception as e:
        print(f"An error occurred: {e}")

def append_content(file_lines, marker, content_to_append):
    for index, line in enumerate(file_lines):
        if  line.startswith(marker):
            file_lines.insert(index + 1, content_to_append + '\n')
            break
    return file_lines
def delete_content(file_lines,content_to_delete):
    file_lines = [line for line in file_lines if line.strip() != content_to_delete.strip()]
    return file_lines

haproxy_ip = '4.7.147.112'  # Replace with the public IP address of the target machine
haproxy_username = 'root'        # Replace with the username for the target machine

file_path = '/etc/haproxy/haproxy.cfg'  # Replace with the path to the .cfg file on the remote machine
search_string = 'backend http_back'  # The section header after which you want to append content



#main funtion
if __name__ == "__main__":

    while True:
        check_system_usage()
        time.sleep(5)  # check every 5 seconds

