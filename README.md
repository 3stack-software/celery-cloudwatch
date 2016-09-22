#Celery CloudWatch

Monitor your [celery](http://www.celeryproject.org/) application from within [AWS CloudWatch](http://aws.amazon.com/cloudwatch/)!

##Metrics

The following events are tallied per task:

 * CeleryEventSent
 * CeleryEventStarted
 * CeleryEventSucceeded
 * CeleryEventFailed

You can then see how many tasks/day, tasks/week etc are being completed.

Also, we record the total waiting/running per task:

 * CeleryNumWaiting
 * CeleryNumRunning

Also, statistics on task duration are sent in the metrics:

 * CeleryQueuedTime
 * CeleryProcessingTime

These metrics are sent with all supported stats (No. Events, Sum, Max, Min), allowing you to gain insight into your task processing and match requests and capacity.


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

    (Note: Alternatively, you can set up a `User` with the same policy and provide access details that way)

2. Install via `python-pip` (and upgrade pip & boto)

    ```sh
    sudo apt-get install -y python-pip
    sudo pip install --upgrade pip boto

    # Install directly
    sudo pip install celery-cloudwatch

    # OR, install in a virtualenv
    sudo apt-get install -y python-virtualenv
    mkdir /var/python-envs
    virtualenv /var/python-envs/ccwatch
    source /var/python-envs/ccwatch/bin/activate
    pip install celery-cloudwatch
    ```

3. Create your own `boto.cfg` at `/etc/boto.cfg`-

    ```
    [Credentials]
    # if not using an IAM Role - provide aws key/secret
    aws_access_key_id = xxx
    aws_secret_access_key = yyy

    [Boto]
    cloudwatch_region_name = my-region
    cloudwatch_region_endpoint = monitoring.my-region.amazonaws.com

    ```

4. Create your own config file in `/etc/ccwatch.yaml`

    ```
    ccwatch:
      broker: null
      camera: celery_cloudwatch.CloudWatchCamera
      verbose: no
    camera:
      frequency: 60.0
      verbose: no
    cloudwatch-camera:
      dryrun: no
      namespace: celery
      tasks:
        - myapp.mytasks.taskname
        - myapp.mytasks.anothertask
        - myapp.mytasks.thirdtask
        - name: myapp.secondarytasks
          dimensions:
            task: myapp.secondarytasks
            customDim: value
        - name: myapp.tertiarytasks
          dimensions:
            task: myapp.tertiarytasks
            customDim: value

    ```

5. Install upstart

    Create a file `/etc/init/celery-cloudwatch.conf`-

    ```
    description "Celery CloudWatch"
    author "nathan muir <ndmuir@gmail.com>"

    setuid nobody
    setgid nogroup

    start on runlevel [234]
    stop on runlevel [0156]

    exec /var/python-envs/ccwatch/bin/ccwatch
    respawn
    ```

    then-

    ```sh
    sudo initctl reload-configuration
    sudo service celery-cloudwatch start
    ```


6. Start Celery your celery workers with the `-E` (or `CELERY_SEND_EVENTS=1` and `CELERY_TRACK_STARTED=1`) options, and, start celery clients with `CELERY_SEND_TASK_SENT_EVENT=1`

7. All done! head over to your CloudWatch monitoring page to see the results!
