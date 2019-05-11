import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event,context):
    
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:926301813786:deployPortfolioTopic')
    
    try:
        
        s3 = boto3.resource('s3')
        
        portfolio_bucket = s3.Bucket("portfolio.mingeegee.com")
        
        
        build_bucket = s3.Bucket("portfoliobuild.mingeegee.com")
        
        portfolio_zip = StringIO.StringIO()
        
        build_bucket.download_fileobj('portfoliobuid.zip',portfolio_zip)
        
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                    ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print "job done!"
        topic.publish(Subject="AWS portfolio deployed",Message="Deployment Success!")
    except:
        topic.publish(Subject="AWS deployment failed",Message="Deployment Failed")
        raise
    
    return "Hello Lambda!"