Universal Item Picker
====================

> [!NOTE]
> **Archived, last changed in December 2016.** This 2016 project stored a user's records in a graph and answered natural language queries over them. It is kept for history and is not run anywhere.
>
> **Today's replacements:** graph and entity models live in [base-tdb-models](https://github.com/TalkingDB/base-tdb-models), the knowledge graph store and query parser in [package-parse-tree](https://github.com/TalkingDB/package-parse-tree), and natural language search over a store's records in [module-ecommerce-ai](https://github.com/TalkingDB/module-ecommerce-ai).

1. Takes input of user's database, sends them to CommandNet Processor to understand what each record means
2. Stores the CommandNet Processor's output of user's database in a persistent graph store for future retrieval
3. Takes input of user's Natural Language query, sends it to CommandNet Processor to understand what the query means
4. Searches for user's search query inside persistant graph store, and returns records that match with query

TODO : Currently Universal Item Picker only 'picks or selects' records. It does not updates records. Update training of CommandNet Processor such that it is able to identify 'update' queries, and later add the support of updating graph store in Universal Item Picker (or maybe rename this project - because it is not longer just 'picking' records but updating them too)

LICENSE

This program has been made available in under the terms of the GNU Affero General Public License (AGPL). See individual files for details.
