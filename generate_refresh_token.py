from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger',
          'https://www.googleapis.com/auth/blogger.readonly']


def main():
    file_name = input("Enter your Google Credits file path or file name:> ")
    flow = InstalledAppFlow.from_client_secrets_file(
        file_name, SCOPES)
    credentials = flow.run_local_server()
    print(credentials.refresh_token)


main()
