function lcs(lcstest, lcstarget) {
	//http://cache.mifio.com/javascript002.html
 matchfound = 0
 lsclen = lcstest.length
  for(lcsi=0; lcsi<lcstest.length; lcsi++){
   lscos=0
    for(lcsj=0; lcsj<lcsi+1; lcsj++){
     re = new RegExp("(?:.{" + lscos + "})(.{" + lsclen + "})", "i");
     temp = re.test(lcstest);
     re = new RegExp("(" + RegExp.$1 + ")", "i");
      if(re.test(lcstarget)){
       matchfound=1;
       result = RegExp.$1;
       break;
       }
     lscos = lscos + 1;
     }
     if(matchfound==1){return result; break;}
    lsclen = lsclen - 1;
   }
  result = "";
  return result;
}


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
				relevance: 0,
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
		
		relevance:function(text){
			this.set("relevance", lcs(text, this.get("label")).length)
		}
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
		},
		
		comparator: function(mentionable1, mentionable2){
			return mentionable2.get("relevance") - mentionable1.get("relevance")
		},
		
		relevance: function(text){
			this.forEach(function(mentionable){
				mentionable.relevance(text)
			})
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
			_.bindAll(this)
			this._viewPointers = []
			this.collection = collection
			this.collection.bind('add', this.addOne, this)
			this.collection.bind('reset', this.reset, this)
			this.collection.bind('all', this.render, this)
			this.collection.bind('remove', this.removeOne, this)
			//List element on DOM that this view is bound to
			this.list = list
			
			console.log(this.collection)
		},
		
		addOne: function(mentionable) {
			var view = new MentionableView({model: mentionable})
			this._viewPointers[mentionable.cid] = view
			this.list.append(view.render().el)
		},
		
		reset: function() {
			this.list.empty()
			this._viewPointers = []
			this.collection.each(this.addOne);
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
	
	function calculateRelevance(){
		console.log("recalculating")
		mentionables.relevance($("#id_text").val())
		mentionables.sort()
	}
	
	var lazyCalculateRelevance = _.debounce(calculateRelevance, 300, true)
	
	
	$("#id_text").bind("change keyup", lazyCalculateRelevance)
	
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
		calculateRelevance()
		if (!uri_set_empty){
			$("#didyoumention").removeAttr("hidden")
		}
		form.submit(function(e){
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
