for ((i=1;i<=200;i++)); 
do
# Replace these urls with your URLs
# Target existing service’s routes
curl http://trave-ec2se-17kf2574xmb2p-8905181793902d76.elb.us-west-2.amazonaws.com -A dd-test-scanner-log;
# Target non existing service’s routes
curl http://trave-ec2se-17kf2574xmb2p-8905181793902d76.elb.us-west-2.amazonaws.com/bad -A dd-test-scanner-log;
done