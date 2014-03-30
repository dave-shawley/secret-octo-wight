Information Model
=================
The information model is composed of a number of related entities.
Each entity is exposed across an HTTP API as representations in a
variety of formats (e.g., JSON documents) and manipulated using HTTP
resources.  The same entities are implemented as Python classes.
This section describes the abstract information model that ties it
all together.

The Family Tree information model differs from other genealogical models
in that it contains three entities and simple relationships between the
entities.  For example, families are not explicitly modeled.  Instead,
a family is designated by a *family event* that is attached to all of
the people in the family.  The event is backed up (or derived from) a
*census source*.  The application can derive a family record for any
person by examining a filtered list of events.


Entities
--------

Person
~~~~~~
This is the primary entity in the model.  It represents a single person
in a historical sense.  A person can, and usually does, have different
names in various documents.  For example, census data is recorded orally
so names are spelled phonetically which results in variations.  This
can become quite problematic since it is common to use a person's name
as the means of identifying him or her.  The information model includes
a common or display name for a person that is independent of the name
of the person on a historical document.

common name
    The display name associated with this person.  This is not required
    to be unique.

birth date
    The currently accepted date of birth.  This value is calculated
    based on **birth** events.

date of death
    The currently accepted date of death.  This value is calculated
    based on **death** events.

events
    List of events that are associated with this person.


Source
~~~~~~
A source is a historical record associated with another entity.  Sources
form the basis for truths and act as evidence.

source type
    An open-ended enumerated type field.

document
    An optional link to a electronic document that acts as the source.

physical document
    An optional citation to the physical source document.

date
    Historical date of this source.


Event
~~~~~
A event is a historically significant occurrence that relates one or more
people.  An event is described by one or more sources.  The date that
an event occurred at is calculated by selecting the date of the most
appropriate source.

event type
    A relatively open-ended, enumerated field.

sources
    The list of sources that describe this event.

preferred source
    The *most appropriate* source.
