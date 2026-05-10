#ifndef _VECTOR_H
#define _VECTOR_H


typedef struct Node
{
		void *element;
		struct Node *next;
		struct Node *previous;
} Node;

typedef struct Vector
{
	int length;
	Node * head;
}Vector;

Vector *create();
void deleteVector(Vector* vector);
void addElement(Vector*, void *);
void removeElementAt(Vector*, int);
void* elementAt(Vector*, int);
int isEmpty(Vector*);
int size(Vector*);
int getIndexOf(Vector*, void*);

#endif