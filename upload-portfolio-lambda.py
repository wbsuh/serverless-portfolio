import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event,context):
    
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:926301813786:deployPortfolioTopic')
    
    
    location = {
        "bucketName": "portfoliobuild.mingeegee.com",
        "objectKey": 'portfoliobuid.zip'
    }
    
    try:
        job = event.get("CodePipline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
                    
        print "Building Portfolio from " + str(location)            
        
        s3 = boto3.resource('s3')
        
        portfolio_bucket = s3.Bucket("portfolio.mingeegee.com")
        
        
        build_bucket = s3.Bucket(location['bucketName'])
        
        portfolio_zip = StringIO.StringIO()
        
        build_bucket.download_fileobj(location['objectKey'],portfolio_zip)
        
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                    ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print "job done!"
        topic.publish(Subject="AWS portfolio deployed",Message="Deployment Success!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
            
            
    except:
        topic.publish(Subject="AWS deployment failed",Message="Deployment Failed")
        
    
    return "Hello Lambda!"