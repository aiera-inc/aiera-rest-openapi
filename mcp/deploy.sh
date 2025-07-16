#!/bin/bash

# Aiera MCP Server Deployment Script
# This script deploys the MCP server to AWS Lambda using SAM

set -e

# Configuration
STACK_NAME="aiera-mcp-server"
REGION="us-east-1"
STAGE="dev"
SAM_S3_BUCKET=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command -v sam &> /dev/null; then
        print_error "SAM CLI is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Function to validate AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_status "AWS credentials are valid."
}

# Function to get or create S3 bucket for SAM deployments
setup_s3_bucket() {
    if [ -z "$SAM_S3_BUCKET" ]; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        SAM_S3_BUCKET="aiera-mcp-sam-deployments-${ACCOUNT_ID}-${REGION}"
    fi
    
    print_status "Using S3 bucket: $SAM_S3_BUCKET"
    
    if ! aws s3 ls "s3://$SAM_S3_BUCKET" &> /dev/null; then
        print_status "Creating S3 bucket: $SAM_S3_BUCKET"
        aws s3 mb "s3://$SAM_S3_BUCKET" --region "$REGION"
    fi
}

# Function to get Aiera API key
get_api_key() {
    if [ -z "$AIERA_API_KEY" ]; then
        echo -n "Enter your Aiera API key: "
        read -s AIERA_API_KEY
        echo
    fi
    
    if [ -z "$AIERA_API_KEY" ]; then
        print_error "Aiera API key is required. Please set AIERA_API_KEY environment variable or enter it when prompted."
        exit 1
    fi
}

# Function to build the SAM application
build_app() {
    print_status "Building SAM application..."
    sam build --use-container
}

# Function to deploy the SAM application
deploy_app() {
    print_status "Deploying to AWS Lambda..."
    
    sam deploy \
        --stack-name "$STACK_NAME-$STAGE" \
        --s3-bucket "$SAM_S3_BUCKET" \
        --region "$REGION" \
        --capabilities CAPABILITY_IAM \
        --parameter-overrides \
            AieraApiKey="$AIERA_API_KEY" \
            Stage="$STAGE" \
        --no-fail-on-empty-changeset
}

# Function to get stack outputs
get_outputs() {
    print_status "Getting deployment outputs..."
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$STAGE" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    MCP_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$STAGE" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`McpServerUrl`].OutputValue' \
        --output text)
    
    FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME-$STAGE" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`FunctionName`].OutputValue' \
        --output text)
    
    echo
    print_status "Deployment successful!"
    echo "API Gateway URL: $API_URL"
    echo "MCP Server URL: $MCP_URL"
    echo "Function Name: $FUNCTION_NAME"
    echo
    print_status "You can now use the MCP server at: $MCP_URL"
}

# Function to test the deployment
test_deployment() {
    print_status "Testing deployment..."
    
    # Test the health endpoint
    if curl -s -f "$API_URL/health" > /dev/null; then
        print_status "Health check passed!"
    else
        print_warning "Health check failed - the server might still be starting up."
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -s, --stage STAGE     Deployment stage (dev, staging, prod) [default: dev]"
    echo "  -r, --region REGION   AWS region [default: us-east-1]"
    echo "  -b, --bucket BUCKET   S3 bucket for SAM deployments [auto-generated]"
    echo "  -h, --help           Show this help message"
    echo
    echo "Environment variables:"
    echo "  AIERA_API_KEY        Aiera API key (required)"
    echo
    echo "Examples:"
    echo "  $0                   Deploy to dev stage"
    echo "  $0 -s prod           Deploy to prod stage"
    echo "  $0 -r us-west-2      Deploy to us-west-2 region"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stage)
            STAGE="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -b|--bucket)
            SAM_S3_BUCKET="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate stage
if [[ ! "$STAGE" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Invalid stage: $STAGE. Must be one of: dev, staging, prod"
    exit 1
fi

# Main deployment flow
main() {
    print_status "Starting Aiera MCP Server deployment..."
    print_status "Stage: $STAGE"
    print_status "Region: $REGION"
    echo
    
    check_dependencies
    check_aws_credentials
    setup_s3_bucket
    get_api_key
    build_app
    deploy_app
    get_outputs
    test_deployment
    
    print_status "Deployment complete!"
}

# Run main function
main