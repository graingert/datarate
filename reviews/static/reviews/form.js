$(function(){
	//Mentionable model
	var form = $("#review-form")
	var submitButton = $("#review-form input[type=submit]")
	submitButton.attr("disabled", "disabled")
	
	var Mentionable = Backbone.Model.extend({
		defaults: function() {
			return {
				label: "no label",
				uri: "no uri",
			}
		},
		
		mention: function(){
			mentionables.remove(this)
			mentioned.add(this)
		},
		
		unmention:function(){
			mentioned.remove(this)
			mentionables.add(this)
		},
	})
	
	var uri_set = {}
	var uri_set_empty = true
	
	
	var MentionableList = Backbone.Collection.extend({
		model: Mentionable,
		
		add: function(mentionable){
			if (uri_set.hasOwnProperty(mentionable.uri)){
				return
			}
			uri_set_empty = false
			uri_set[mentionable.get("uri")] = mentionable
			Backbone.Collection.prototype.add.call(this, mentionable)
		},
		
		remove: function(mentionable){
			delete uri_set[mentionable.uri]
			Backbone.Collection.prototype.remove.call(this, mentionable)
		}
	})
	
	var MentionableView = Backbone.View.extend({
		tagName: "li",
		template: Handlebars.compile($("#mentionable-tmpl").html()),
		
		events: {
			"click .mention" : "mention",
			"click .unmention" : "unmention",
		},
		
		initialize: function(){
			this.model.bind('change', this.render, this)
		},
		
		render: function(){
			this.$el.html(this.template(this.model.toJSON()))
			return this
		},
		
		mention: function(){
			this.model.mention()
		},
		
		unmention: function(){
			this.model.unmention()
		},
	})
	
	var MentionListView = Backbone.View.extend({
		
		initialize: function(collection, list) {
			this._viewPointers = []
			
			collection.bind('add', this.addOne, this)
			collection.bind('reset', this.addAll, this)
			collection.bind('all', this.render, this)
			collection.bind('remove', this.removeOne, this)
			this.list = list
		},
		
		addOne: function(mentionable) {
			var view = new MentionableView({model: mentionable})
			this._viewPointers[mentionable.cid] = view
			this.list.append(view.render().el)
		},
		
		addAll: function() {
			collection.each(this.addOne);
		},
		
		removeOne: function(mentionable){
			this._viewPointers[mentionable.cid].remove()
			delete this._viewPointers[mentionable.cid]
		},
	})
	
	var mentionables = new MentionableList;
	var mentioned = new MentionableList;
	
	
	var mentionableView = new MentionListView(mentionables, $("#mentionable-list"))
	var mentionedView = new MentionListView(mentioned, $("#mentioned-list"))
	
	var sparqlRelatedThings = Handlebars.compile($("#sparql-related-things").html())
	var relatedThings = Handlebars.compile($("#related-things").html())
	
	var sparqler = new SPARQL.Service("http://sparql.data.southampton.ac.uk/")
	
	sparqler.setPrefix("foaf", "http://xmlns.com/foaf/0.1/")
	sparqler.setPrefix("dct", "http://purl.org/dc/terms/")
	sparqler.setPrefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
	
	sparqler.setOutput("json")
	sparqler.setMethod("POST")
	
	get_mentionables()
	
	function get_mentionables(){
		var query = sparqler.createQuery()
			
			
		query.query(
			sparqlRelatedThings({uri:$("#thing-link").attr("data-uri")}),
			{
				failure: function(){
					done()
				},
				success: function(json) {

					for(var i=0; i<json.results.bindings.length; i++){
						var item = json.results.bindings[i]
						if (item.thing.type == "uri" && 'name' in item){
							mentionables.add(new Mentionable({ uri:item.thing.value, label:item.name.value}))
						}
					}
					done()
				}
			}
		)
	}
	
	var mentionedInput = $("#review-form input[name=mentioned]")
	
	function addPreviousThings(){
		var uris = []
		try{
			uris = $.parseJSON(mentionedInput.val())
		} catch(err) {

		}
		_.each(uris, function(uri){
			if (uri_set.hasOwnProperty(uri)){
				uri_set[uri].mention()
			}
		})
	}
	
	
	function done(){
		addPreviousThings()
		if (!uri_set_empty){
			$("#didyoumention").removeAttr("hidden")
		}
		form.submit(function(event){
			var uris = []
			mentioned.each(function(mentionable){
				console.log(mentionable)
				uris.push(mentionable.get("uri"))
			})
			mentionedInput.val(JSON.stringify(uris))
			return true	
		})	
		submitButton.removeAttr("disabled")
	}
})
