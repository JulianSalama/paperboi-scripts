Thank you noplay for providigin a great mysql log parser... This script is intended to be used by anyone, and streams your mysql logs to S3 in sequential order. Paperboi.io provides tool to act on those stream of data. Visit paperboi.io in order to learn more.

Installation:
1) clone this repo
2) open up the configuration file, and set up the keys needed for this script to load the logs from your MySQL instance
3) This script uses boto3, make sure the AWS keys are properly set up to upload the logs to your bucket

Next Steps:
Visit paperboi.io to learn what you can do with logs

Licence
Copyright 2018 Julian Salama

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
