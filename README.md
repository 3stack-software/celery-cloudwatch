#Celery CloudWatch

Monitor your [celery](http://www.celeryproject.org/) application from within [AWS CloudWatch](http://aws.amazon.com/cloudwatch/)!

##Metrics

The following events are tallied per task:

 * CeleryTaskEventWaiting
 * CeleryTaskEventRunning
 * CeleryTaskEventCompleted
 * CeleryTaskEventFailed

You can then see how many tasks/day, tasks/week etc are being completed.

Also, statistics on task duration are sent in the metrics:

 * CeleryTaskQueuedTime
 * CeleryTaskProcessingTime

These metrics are sent with all supported stats (No. Events, Sum, Max, Min), allowing you to gain insight into your task processing and match requests and capacity.

Finally, the following metrics are sent as overalls:

 * CeleryQueueSize
 * CeleryRunningTasks



#Getting Started

1. Set up an [IAM Role](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html) for your instance.

    It must include a policy to perform 'PutMetricData', eg:
    ```json
    {
      "Version": "2000-01-01",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "cloudwatch:PutMetricData"
          ],
          "Resource": [
            "*"
          ]
        }
      ]
    }

    ```
    (Note: Alternitavely, you can set up a `User` with the same policy and provide access details that way)

2. Install recent versions of `boto` and `celery`  (via `python-pip`)

    ```sh
    sudo apt-get install -y python-pip
    sudo pip install --upgrade boto
    sudo pip install celery
    ```

3. Copy `celery-cloudwatch` to your server

4. Create your own `boto.cfg`

    ```
    [Credentials]
    # if not using an IAM Role - provide aws key/secret
    aws_access_key_id = xxx
    aws_secret_access_key = yyy

    [Boto]
    cloudwatch_region_name = my-region
    cloudwatch_region_endpoint = monitoring.my-region.amazonaws.com

    ```

5. Write a launch script, `launch.sh` with configured environment variables (you could include them in the next script instead too)
    ```sh
    CELERY_BROKER_URL="amqp://guest@localhost:5672//" \
    TASK_MONITOR_CW_TASK_NAMES=task,names,to,monitor,comma,separated \
    TASK_MONITOR_CW_NAMESPACE=my-custom-aws-namespace \
    TASK_MONITOR_CW_QUEUES=comma-separated-queue-names-default-celery \
    BOTO_CONFIG=myboto.cfg \
    bash bin/task_monitor -c lib.CloudWatchCamera --factory=lib.CloudWatchCameraFactory --freq=60
    ```

6. Install upstart

    Create a file `/etc/init/celery-cloudwatch.conf`
    ```
    description "Celery Cloud Watcher"
    author "nathan muir <ndmuir@gmail.com>"

    start on runlevel [234]
    stop on runlevel [0156]

    chdir /path/to/celery-cloudwatch
    exec /path/to/celery-cloudwatch/launch.sh
    respawn
    ```

    then
    ```sh
    sudo initctl reload-configuration
    sudo service celery-cloudwatch start
    ```


7. Start Celery your celery workers with the `-E` (or `CELERY_SEND_EVENTS=1`) option, and, start celery clients with `CELERY_SEND_TASK_SENT_EVENT=1`

8. All done! head over to your CloudWatch monitoring page to see the results!
