void Grammar::ParseString(vector<GrammarSymbol> str)
{
    int i,j,k,l,temp;
    vector<GrammarSymbol> parse_stack;
    GrammarSymbol dollar;
    dollar.content="$";
    dollar.type="dollar";
    parse_stack.push_back(dollar);
    
    str.push_back(dollar);
    parse_stack.push_back(this->rules[0].lhs);
    cout<<"\n";
    for(l=0; l<parse_stack.size(); l++)
    {
        cout<<parse_stack[l].content;
    }
    // DONE
    for(i=0; i<str.size(); i++)
    {
        if(parse_stack[parse_stack.size()-1].type=="Terminal"||parse_stack[parse_stack.size()-1].type=="dollar")
        {
           cout<<"\t\t";
            for(temp=i; temp<str.size(); temp++)
            {
                cout<<str[temp].content;
            }
            if(str[i].content==parse_stack[parse_stack.size()-1].content)
            {
                if(str[i].content=="$")
                {
                    cout<<"\nAccepted";
                    return;
                }
                else
                {
                    parse_stack.pop_back();
                }
            }
        }
        else if(parse_stack[parse_stack.size()-1].type=="NonTerminal")
        {
          cout<<"\t\t";
            for(temp=i; temp<str.size(); temp++)
            {
                cout<<str[temp].content;
            }
            for(j=0; j<NonTerminals.size(); j++)
            {
                if(parse_stack[parse_stack.size()-1].content==NonTerminals[j].content)
                    break;
            }
            for(k=0; k<Terminals.size(); k++)
            {
                if(str[i].content==Terminals[k].content)
                    break;
            }
            if(j<NonTerminals.size()&&k<Terminals.size()||j<NonTerminals.size()&&str[i].content=="$")
            {
                parse_stack.pop_back();
                if(this->ParseTable[j+1][k+1].size()==0)
                {
                    cout<<"\nError accepting string";
                    return;
                }
                else
                {
                    if(this->ParseTable[j+1][k+1].size()==1 && this->ParseTable[j+1][k+1][0].content=="epsilon")
                    {
                        i--;
                    }
                    else
                    {
                        for(l=this->ParseTable[j+1][k+1].size()-1; l>=0; l--)
                        {
                            parse_stack.push_back(ParseTable[j+1][k+1][l]);
                        }
                        i--;
                    }
                }
            }
            else
            {
                cout<<"\nError accepting string";
                return;
            }
        }
        cout<<"\n";
        for(l=0; l<parse_stack.size(); l++)
        {
            cout<<parse_stack[l].content;
        }
    }
}
