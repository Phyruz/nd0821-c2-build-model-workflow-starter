#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import tempfile
import wandb
import pandas as pd



logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    logger.info(f"Downloading input artifact: {args.input_artifact}")
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    ## Cleaning steps
    # Drop price outliers
    logger.info(f"Cleaning step 1: retain items with price value \
    between {args.min_price} and {args.max_price} dollars")
    df = df[df["price"].between(args.min_price, args.max_price)]

    # Drop minimum_nights outliers
    logger.info(f"Cleaning step 2: retain items with minimum_nights value \
    between {args.min_nights} and {args.max_nights} dollars")
    df = df[df["minimum_nights"].between(args.min_nights, args.max_nights)]

    # Convert last_review to datetime
    logger.info("Cleaning step 3: convert last_review to datetime")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save file as CSV and load W&B artifact
    logger.info(f"Saving clean sample in local directory")
    df.to_csv("clean_sample.csv", index=False)

    logger.info(f"Uploading {args.output_artifact} to Weights & Biases")
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)

    artifact.wait()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Name of the input artifact contained in W&B",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name of the output artifact to be uploaded in W&B",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="The type for the output artifact",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="A description for the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Min price to consider when filtering during data cleaning step",
        required=False
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Max price to consider when filtering during data cleaning step",
        required=False
    )

    parser.add_argument(
        "--min_nights", 
        type=int,
        help="Min nights to consider when filtering during data cleaning step",
        required=False
    )

    parser.add_argument(
        "--max_nights", 
        type=int,
        help="Max price to consider when filtering during data cleaning step",
        required=False
    )


    args = parser.parse_args()

    go(args)
