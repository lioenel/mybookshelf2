import {LogManager, inject} from 'aurelia-framework';
import {ApiClient} from 'lib/api-client';
import {Configure} from 'lib/config/index';
import {WSClient} from 'lib/ws-client';
import {EventAggregator} from 'aurelia-event-aggregator';
import {Notification} from 'lib/notification';

let logger=LogManager.getLogger('upload');

function hex(buffer) {
  var hexCodes = [];
  var view = new DataView(buffer);
  for (var i = 0; i < view.byteLength; i += 4) {
    // Using getUint32 reduces the number of iterations needed (we process 4 bytes each time)
    var value = view.getUint32(i)
    // toString(16) will give the hex representation of the number without padding
    var stringValue = value.toString(16)
    // We use concatenation and slice for padding
    var padding = '00000000'
    var paddedValue = (padding + stringValue).slice(-padding.length)
    hexCodes.push(paddedValue);
  }

  // Join all the hex strings into one
  return hexCodes.join("");
}

@inject(ApiClient, WSClient, Configure, EventAggregator, Notification)
export class Upload {
  fileOK=false;
  uploading=false;
  checking=false;
  uploadError=null;
  uploadId=null;

  constructor(client, wsClient, config, event, notif) {
    this.client=client;
    this.wsClient=wsClient;
    this.config=config;
    this.event = event;
    this.notif = notif;
  }
  upload() {
    this.fileOK=false;
    this.checking=false;
    this.uploading =  true;
    logger.debug(`Uploading file`);
    let formData= new FormData(document.getElementById('file-upload-form'))
    this.client.upload(formData)
      .then(data => {
        if (data.error) {
          this.uploadError=`Upload error: ${data.error}`;
          logger.error(`Upload error: ${data.error}`);
          this.uploading = false;
        } else {
          logger.debug(`File uploaded ${JSON.stringify(data)}`);
          let origName =  document.getElementById('file-input').value;
          this.wsClient.extractMeta(data.file, origName)
            .then(taskId => {
              logger.debug(`Task ID ${taskId} for file ${data.file}`);
              this.event.subscribe('metadata-ready', result => {
                if (taskId === result.taskId) {
                  this.uploading = false;
                  this.notif.markDone(taskId);
                  window.location.href='#/upload-result/'+result.result;

                }
              });
              this.event.subscribe('metadata-error', result => {
                if (taskId === result.taskId) {
                this.uploading = false;
                this.uploadError = `Error in metadata: ${result.error}`;
              }
              });
            })
            .catch(err => {
              logger.error(`Error when extracting metadata: ${err}`);
              this.uploading = false;
              this.uploadError = `Error in metadata: ${err}`;
            });
        }
      })
  }

  checkFile() {
    this.checking=true;
    this.uploading=false;
    this.fileOK=false;
    this.uploadError=null;
    this.uploadId=null;

    let files=document.getElementById('file-input');
    if (files.files.length < 1) {
      this.checking=false;
      return;
    }
    let file=files.files[0]
    if (file.size > this.config.get('maxUploadSize')) {
      this.uploadError='Are you mad? This file is just too big for ebook!';
      this.checking=false;
      return
    }
    var fileInfo = {
      mime_type:file.type,
      size:file.size,
      hash: null
    }
    let reader=new FileReader()
    reader.onload = () => crypto.subtle.digest("SHA-1", reader.result)
      .then(val => {
        fileInfo.hash=hex(val);
        logger.debug('File info '+JSON.stringify(fileInfo));
        this.client.checkUpload(fileInfo)
          .then( () => {
            this.checking=false;
            this.fileOK=true;
          })
          .catch( err => {
            this.checking=false;
            logger.error(`File check error`, err);
            this.uploadError=`Check error: ${err}`
          })
      });
    reader.readAsArrayBuffer(file);
    logger.debug(`Checking file ${file.name}`)
  }
}
