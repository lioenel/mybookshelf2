import {inject, bindable, computedFrom, LogManager} from 'aurelia-framework';
import {ApiClient} from 'lib/api-client';
const logger = LogManager.getLogger('search');

@inject(ApiClient)
export class Author {
  _loader;
  @bindable filter;
  author;

  constructor(client) {
    this.client=client;
  }

  activate(params)  {
    logger.debug('Author activated with '+JSON.stringify(params));
    this.id=decodeURIComponent(params.id);
    this.client.getOne('authors', params.id). then(data => {this.author=data; logger.debug('Loaded author'+JSON.stringify(data))})

    this.updateLoader()
  }

  filterChanged() {
    logger.debug('Filter changed to '+ this.filter);
    this.updateLoader()
  }

  updateLoader() {
    this._loader = this.client.authorBooks.bind(this.client, this.id, this.filter);
  }

  @computedFrom('_loader')
  get loader() {
    return this._loader;
  }

}
