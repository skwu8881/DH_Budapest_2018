Rails.application.routes.draw do
  get '/', to: 'intro#index'

  get 'textmining', to: 'textmining#index'
  post 'textmining/submit_article', to: 'textmining#submit_article'

  get 'history', to: 'history#index'
end
