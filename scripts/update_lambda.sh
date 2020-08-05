cd ..
if [ "$1" == "-d" ]; then
  rm function.zip
  echo "d flag found"
  cd venv/lib/python3.8/site-packages/
  zip -r9 ${OLDPWD}/function.zip .
  cd $OLDPWD
fi
zip -g -r9 function.zip nba/
zip -g function.zip handler.py
aws lambda update-function-code --function-name nba-matchups-daily --zip-file fileb://function.zip