#Copyright (c) 2012, Miguel Araujo
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:

 #* Redistributions of source code must retain the above copyright notice, this
   #list of conditions and the following disclaimer.

 #* Redistributions in binary form must reproduce the above copyright notice,
   #this list of conditions and the following disclaimer in the documentation
   #and/or other materials provided with the distribution.

 #* Neither the name of Miguel Araujo nor the names of its contributors
   #may be used to endorse or promote products derived from this software
   #without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#https://gist.github.com/893408

"""
jQuery templates use constructs like:

{{if condition}} print something{{/if}}

This, of course, completely screws up Django templates,
because Django thinks {{ and }} means something.

Wrap {% verbatim %} and {% endverbatim %} around those
blocks of jQuery templates and this will try its best
to output the contents with no changes.

This version of verbatim template tag allows you to use tags
like url {% url name %} or {% csrf_token %} within.
"""

from django import template

register = template.Library()


class VerbatimNode(template.Node):
    def __init__(self, text_and_nodes):
        self.text_and_nodes = text_and_nodes
    
    def render(self, context):
        output = ""

        # If its text we concatenate it, otherwise it's a node and we render it
        for bit in self.text_and_nodes:
            if isinstance(bit, basestring):
                output += bit
            else:
                output += bit.render(context)

        return output

@register.tag
def verbatim(parser, token):
    text_and_nodes = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('{{')
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_TEXT:
            text_and_nodes.append(token.contents)

        elif token.token_type == template.TOKEN_BLOCK:
            try:
                command = token.contents.split()[0]
            except IndexError:
                parser.empty_block_tag(token)

            try:
                compile_func = parser.tags[command]
            except KeyError:
                parser.invalid_block_tag(token, command, None)
            try:
                node = compile_func(parser, token)
            except template.TemplateSyntaxError, e:
                if not parser.compile_function_error(token, e):
                    raise
        
            text_and_nodes.append(node)

        if token.token_type == template.TOKEN_VAR:
            text_and_nodes.append('}}')
           
    return VerbatimNode(text_and_nodes)
