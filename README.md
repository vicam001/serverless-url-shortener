# url-shortener

1.Dependencies and Layers


- To work in a local python environment, run in the terminal:

https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/manage-sam-cli-versions.html#manage-sam-cli-versions-install-virtual

```bash
python3 -m venv venv
source venv/bin/activate
```
To exit the virtual env:
```bash
deactivate
```

- To install the dependencies, go to the function's folder

```bash
cd src/functions/urlShortener
pip install -r requirements.txt
```

- To update the SAM CLI

```bash
sudo installer -pkg /Users/vicente/Downloads/aws-sam-cli-macos-x86_64.pkg -target /
```

- To uninstall the SAM CLI
```bash
which sam
sudo rm -rf /Library/Frameworks/Python.framework/Versions/3.8/bin/sam
```

- To configure a Layer with the dependencies:

```bash
pip install -r src/functions/callOpenAI/requirements.txt -t src/layers/callOpenAI/python
```

- To run a function locally:

```bash
sam local invoke "CreateOrder" --event ./events/extractedOrderData.json --env-vars env.json --profile SuperAdmin
```

- To deploy the Stack

```bash
sam deploy --config-env dev --profile SuperAdmin
sam deploy --config-env prod --profile SuperAdmin
sam deploy --guided
```

- Copy all files from one S3 Bucket to another S3 Bucket:

```bash
aws s3 sync s3://order-processing-app-dev-eu-west-1-order-processing-dev-copy s3://order-processing-app-dev-eu-west-1-order-processing-dev --storage-class STANDARD --profile SuperAdmin
```

# LlamaIndex

- Regions: https://docs.cloud.llamaindex.ai/regions
