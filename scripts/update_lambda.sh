if [ "$1" == "-d" ]; then
  echo "d flag found"
  cd venv/lib/python3.7/site-packages/
  zip -r9 ${OLDPWD}/function.zip .
  cd $OLDPWD
fi
zip -g -r9 function.zip nba/
zip -g function.zip handler.py
aws lambda update-function-code --function-name nab-matchup-ranker --zip-file fileb://function.zip