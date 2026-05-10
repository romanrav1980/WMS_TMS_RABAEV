#include "stdafx.h"
#include "vector.h"


Vector* create()
{
	Vector * vector = new Vector;//(Vector *)allocate(sizeof(Vector));
	if (vector == NULL)
	{
		return NULL;
	}
	vector->length = 0;
	vector->head = NULL;
	return (Vector *)vector;
}

void deleteVector(Vector* vector)
{
	if(vector==NULL)
		return;
	
	while(vector->length>0)
		removeElementAt(vector,vector->length-1);
	
	//Free(vector);
	delete vector;
	
	vector=NULL;
}

// function to add an element to the list (equivalent to the java Vector.addElement())
void addElement(Vector *vector, void *data)
{
	Node* prevNode = vector->head;
	Node* elementNode=NULL;

    if(!vector)
    {
        return;
    }
	elementNode = new Node;//(Node*)allocate(sizeof(Node));
	elementNode->element = data;
	elementNode->next = NULL;
	elementNode->previous = NULL;

	// in case the element to be added is the first element
	if (vector->length==0)
	{
		vector->head = elementNode;
	}
	else
	{	// loop till the end of list is reached
		while(prevNode->next!=NULL)
			prevNode = prevNode->next;

		prevNode->next = elementNode;
		elementNode->previous = prevNode;
	}
	vector -> length++;
}

// function to remove an element from the list, identified by the index number (equivalent to the Vector.removeElementAt())
void removeElementAt(Vector *vector, int index)
{
	int i = 0;
	Node *tempNode=NULL;
	
	// check if the index is less than zero, that is negative index error
	if (index < 0)
	{
		return;
	}

	// check if the index falls inside the length of the list, else it is a out of range error
	if(index >= vector->length)
	{
		return;
	}
	if(vector->length==1) // index==0
	{
		//Free(vector->head);
		delete vector->head;
		vector->head=NULL;
		vector->length--;
		return;
	}

	tempNode = vector->head;
	// check if the index is the head of the list.
	if(index==0)
	{
		vector->head = vector->head->next;
		vector->head->previous = NULL;
		vector->length--;
		//Free(tempNode);
		delete tempNode;
		tempNode = NULL;
		return;
	}
	// check is the index is the last node
	if(index == vector->length - 1)
	{
		while(tempNode->next!=NULL)
		{
			tempNode = tempNode->next;
		}
		tempNode->previous->next = NULL;
		//Free(tempNode);
		delete tempNode;
		tempNode=NULL;
		vector->length--;
		return;
	}
	for(;i<vector->length;i++)
	{
		if(index==i)
		{
			tempNode->previous->next = tempNode->next;
			tempNode->next->previous = tempNode->previous;
			vector->length--;
			//Free(tempNode);
			delete tempNode;
			tempNode=NULL;
			return;
		}
		tempNode = tempNode->next;
	}
}

int getIndexOf(Vector* vector, void* data)
{
	Node* tempNode = vector->head;
	int i = 0;

	while(tempNode!=NULL)
	{
		if(tempNode->element==data)
			return i;
		tempNode = tempNode->next;
		i++;
	}
	return -1;
}


// function to obtain the element at a given index (equivalent to the Vector.elementAt())
void* elementAt(Vector* vector, int index)
{
	int i = 0;
	Node* tempNode = vector->head;

	// checking for negative index reference
	if(index < 0)
	{
		return NULL;
	}
	// checking for index out of range error
	if (index >= vector->length)
	{
		// Index out of range
		return NULL;
	}
	for(;i<vector->length; i++)
	{
		if (i==index)
			return (void*)tempNode->element;
		tempNode = tempNode->next;
	}
	return NULL;
}

int isEmpty(Vector *vector)
{
	if(size(vector))
		return FALSE;
	else
		return TRUE;
}

int size(Vector* vector)
{
	if(vector)
		return vector->length;
	else
		return 0;
}

