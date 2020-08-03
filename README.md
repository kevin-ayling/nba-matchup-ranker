# nba-matchup-ranker


aws lambda add-permission \
--function-name nab-matchup-ranker \
--statement-id dailyCWpermission \
--action 'lambda:InvokeFunction' \
--principal events.amazonaws.com \
--source-arn arn:aws:events:us-east-1:557026794806:rule/NBAdailyTrigger