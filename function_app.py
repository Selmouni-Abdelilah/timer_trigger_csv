import  datetime
import  logging
import  os
import  tempfile
import  azure.functions  as  func
import  csv
from    azure.storage.fileshare import ShareFileClient, ShareDirectoryClient

def  write_csv_file(file_path,  data):
    try:
        with  open(file_path,  'a',  newline='')  as  csv_file:
            csv_writer = csv.writer(csv_file)
            for  row  in  data:
                csv_writer.writerow(row)
    except  Exception  as  e:
        logging.error(f"Error writing to CSV file: {e}")
app = func.FunctionApp()
@app.schedule(schedule="0 */2 * * * *", arg_name="mytimer", run_on_startup=True,use_monitor=False) 

def timer_trigger(mytimer:  func.TimerRequest)  ->  None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if  mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s',  utc_timestamp)
    function_directory = os.getcwd()
    file_name = 'timestamp.csv'
    local_path = tempfile.gettempdir()
    file_path = os.path.join(local_path, file_name)
    csv_data = [[utc_timestamp]]
    write_csv_file(file_path,  csv_data)
    conn_string ="DefaultEndpointsProtocol=https;AccountName=destinationfileshare;AccountKey=vjD7ggihKeLBcnruKEtosfSSOotALfW9YSOg2Bw/QkjpsO69H7Z0WW0fP1YXmNYzOOVj2rv/dcZr+AStNr4vuw==;EndpointSuffix=core.windows.net"
    share_directory_client = ShareDirectoryClient.from_connection_string(conn_str=conn_string, 
                                                            share_name="timerfileshare",
                                                            directory_path="outgoing")

    file_client = ShareFileClient.from_connection_string(conn_str=conn_string, share_name="timerfileshare", file_path="outgoing/file.csv")

    # Operation on file here
    f = open(file_path, 'rb')
    string_to_upload = f.read()
    f.close()

    #Upload file
    logging.info('uploading file...')
    file_client.upload_file(string_to_upload)
    logging.info('file uploaded successfully...')
