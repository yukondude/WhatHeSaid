Title: Tame Visual Basic with IDL
Status: hidden
Save_as: what-he-wrote/tame-visual-basic-with-idl/index.html

<p><em>This is an obsolete article about an obsolete technology, but if that doesn't somehow deter you, please read on. Don't expect the links to work though.</em></p>
<h3>Summary</h3>
<p>This article assumes you are familiar with Visual Basic, COM, and IDL. Sample source code to accompany this article is available in the attached <a href="/heap/tame-vb-with-idl.zip">tame-vb-with-idl.zip</a> file.</p>
<p>Serious COM development in Visual Basic is hampered by the language's simplified presentation of fundamental COM concepts. Interface versioning problems are the most expensive result of delegating development responsibility to the Visual Basic IDE. The Interface Definition Language is intended to give developers precisely that level of control required for successful COM software projects. The article argues for, and demonstrates, the correct way to use IDL to define interfaces for VB classes to evade these versioning problems. Other benefits of the approach, as well as the shortcomings, are also described.</p>
<p>Dave Rogers is top dude at <a href="http://yukondude.com/">yukon dude software</a>. During the late 1990s, he was co-creator of the Combat COM course and developer community in Toronto, Ontario. He wrote this article while employed as a software architect at FMC Software Consulting Inc.</p>
<p>Since this was first written, an article by Brian Randell and Ted Pattison, <em>Visual Basic Design-Time Techniques to Prevent Runtime Version Conflicts</em>, was published in the January 2000 issue of <em>Microsoft Systems Journal</em> (later, <em>MSDN Magazine</em>). That article presents many of the same techniques described here, and serves to reinforce the many benefits of this approach to Visual Basic COM development.</p>
<h3>Introduction</h3>
<p>Of all the languages that support the Component Object Model (COM), none gives developers the "just get it done" power of Microsoft® Visual Basic®. Visual Basic frees developers from the tedious bookkeeping of low-level COM programming, while encouraging them to concentrate on the actual logic of the application. Win-win, as the suits say.</p>
<p>Unfortunately, VB is <em>so successful</em> at concealing COM's inner workings that, for any but the most trivial of projects, the concealment strategy backfires. To prove my point, how many VB developers recognize the following message box?</p>
<div class="captioned-image"><img src="/heap/tame-vb-with-idl.gif" alt="Aaaaaaargh!"><p>Figure 1: an all too common sight.</p></div>
<p>Anyone who has worked with the language for more than 10 minutes will have seen this error. Accomplished developers will know they need to double-check their compatibility settings and selectively recompile parts of their application. Less experienced developers will recompile anything and everything and hope for the best. Both will curse imaginatively.</p>
<p>As most know, this error message stems from mismatched GUIDs. At some point in the past, a server class was changed and recompiled without the binary compatibility option set, and VB generated new GUIDs for the class's coclass and interfaces. Unaware of this change, the client code attempts to create the object using the old GUID and fails. Fixing the problem involves, at a minimum, recompiling the client code.</p>
<p>The traditional way to deal with this problem is to rigorously control VB's compatibility options. Aside from the Visual Basic documentation, there are a number of technical articles that explain these options and how to use them throughout a project's lifecycle. I've listed a few such references in the bibliography that follows at the end of this article.</p>
<p>The fundamental drawback of these techniques is that you must still rely upon VB to generate and preserve the interface, coclass, and type library GUIDs. You're also trusting that every other member of the development team will agree to play by the same rules. And if you should happen to be a contractor who supplies software to other developers, and they later forget or ignore the rules, whom do you suppose will be blamed for our old friend, run-time error 429?</p>
<p>I should add that, from a strictly purist viewpoint, you're also unwittingly ceding to VB's worldview of "one class, one interface," a decidedly un-COM-like mindset.</p>
<p>The solution I propose, and one we've followed for some time now, is to explicitly define the application's COM interfaces using the Interface Definition Language (IDL). This is by no means an original idea, but when I started digging a little deeper into the issue, I couldn't find any literature that described how I might employ the technique on a large scale, or what the pitfalls might be. That was almost two years ago, and in the time since my coworkers and I have amassed a considerable repository of tips and stratagems for using VB and IDL together, as well as a list of hazards that can blindside the unwary.</p>
<p>Regardless of how I have presented this practice in the past, I am usually rebuffed initially with the remark that "IDL is too hard," or "our project isn't big enough to justify the extra work." Simply put: IDL is not as pretty as Visual Basic code, but you'll find that the OLE-Automation flavour of the IDL that VB can implement is almost a direct translation from the class declaration syntax to which you're accustomed.</p>
<p>Even more simply put: If you don't think your project is big enough, invite me back when your integration testing phase begins. Those that have enthusiastically latched on to the concept from the beginning are typically the veteran VB developers who have felt the pain of maintaining a distributed application without breaking it at every turn, or who have had to spend a night hacking away at their Registry because VB had littered it with gunk.</p>
<h3>An Example</h3>
<p>So, rather than monotonously listing the rules for using IDL to define interfaces for VB, I'll begin with a simple but representative example. Afterwards, I'll describe the more general instructions and exceptions.</p>
<p>There isn't room here to explain the Interface Definition Language in any depth, so I'll assume that you're at least moderately familiar with its syntax. Refer to the article <em>Understanding Interface Definition Language: A Developer's Survival Guide</em> from the August 1998 issue of MSJ (<a href="http://www.microsoft.com/msj">www.microsoft.com/msj</a>) if the topic is new to you.</p>
<h4>Step 1 - Define the interface in IDL</h4>
<p>To begin, let us suppose that we want to create a server class that represents a bank account. This is how its methods might appear if written in Visual Basic:</p>
<pre>Public Function GetBalance() As Currency
Public Sub GetLastTransaction( _
  ByRef TxnDate As Date, _
  ByRef TxnAmount As Currency)</pre>
<p>We'll include these two methods in an interface called IAccount that is a member of the AccountLib type library, and the corresponding IDL will read as follows:</p>
<pre>[ uuid(36872170-4AB7-11d3-B286-00C04F534C97),
  version(1.0) ]
library AccountLib {
  importlib("stdole32.tlb");
  importlib("stdole2.tlb");

  [ object,
    uuid(36872171-4AB7-11d3-B286-00C04F534C97),
    oleautomation ]
  interface IAccount : IUnknown {
    HRESULT GetBalance([out, retval] CURRENCY* pcy);
    HRESULT GetLastTransaction([in, out] DATE* TxnDate,
    [in, out] CURRENCY* TxnAmount);
  };
};</pre>
<p>I've omitted any [helpstring()] attributes but you'll want to include these for the type library, interfaces, and methods. These attributes supply the text that appears in the VB Object Browser.</p>
<p>Something interesting to note about the above example is that I've inherited the IAccount interface directly from the IUnknown interface. Visual Basic-defined interfaces always inherit from IDispatch and therefore are dual interfaces, and to quote <em>Effective COM</em>, "dual interfaces are a hack." You will understand the negative implications of dual interfaces much more clearly at the precise moment that you attempt to return a reference to an object's non-default interface when calling from a late-bound client across apartment boundaries. Read chapter 11, "Typeless languages lose the benefits of COM" from <em>Effective COM</em>, for the complete explanation of that mysterious statement.</p>
<p>Fortunately, VB can happily implement an IUnknown-derived interface and I prefer to define interfaces this way unless there's a compelling argument to do otherwise. If the need does arise, VB is equally able to implement dual interfaces and dispinterfaces.</p>
<h4>Step 2 - Compile the IDL source</h4>
<p>The MIDL command-line compiler (midl.exe) is shipped with many of the Microsoft development tools as well as the Platform SDK. It will produce a number of files that are of interest to C++ developers, but the one we're after is the type library file (*.tlb), a tokenized version of IDL source. The following MIDL command line will generate only this file (you may have to first run the vcvars32.bat batch script to prepare the environment):</p>
<pre>midl /proxy nul /header nul /iid nul
     /dlldata nul AccountLib.idl</pre>
<p>If all is successful, and assuming we had saved the IDL from step 1 in a file named AccountLib.idl, MIDL will spit out a file called AccountLib.tlb. If there was an error, you'll find the MIDL compiler messages to be most unhelpful, but at least the line number of the offending statement is displayed.</p>
<h4>Step 3 - Implement the interface in VB</h4>
<p>Create a new ActiveX DLL server project named AccountServer, with a single class named Account. Select Project | References from the main menu. The type library we have created is not registered yet, so click the Browse button and add a reference to the AccountLib.tlb file. By adding the reference, VB automatically registers the type library.</p>
<p>Inside the code window for the Account class, add the line: Implements IAccount. You can now select the IAccount interface from the object dropdown list at the top of the code window, and its methods from the procedures dropdown list. Doing so will add the skeleton of the methods, and -- with a little wishful thinking -- we can write some dummy code to fill in the methods:</p>
<pre>Implements IAccount

Private Function IAccount_GetBalance() As Currency
  IAccount_GetBalance = 727991.33
End Function

Private Sub IAccount_GetLastTransaction( _
  ByRef TxnDate As Date, _
  ByRef TxnAmount As Currency)
  TxnDate = Now
  TxnAmount = 13500
End Sub</pre>
<p>Compile the project to produce an ActiveX DLL server. Once the server has been compiled, select Project | AccountServer Properties from the main menu and, on the Component tab, select Binary Compatibility and select the compiled AccountServer DLL. Even by using IDL, we haven't completely evaded the compatibility settings, but since we're not exposing any public methods, we can safely make all the changes we want during development. By choosing the binary compatibility setting, we're preventing VB from freely generating new coclass GUIDs.</p>
<h4>Step 4 - Create a client to use the interface</h4>
<p>We'll whip up a standard EXE project named AccountClient containing a module with a Sub Main procedure. This project must also reference the AccountLib type library and by selecting Project | References from the main menu, it will be listed in the Available References listbox since it was registered in step 3. Example code for the Sub Main procedure could look something like the following:</p>
<pre>Sub Main()
  Dim iacc As AccountLib.IAccount
  Dim cur As Currency
  Dim dte As Date

  Set iacc = _
    CreateObject("AccountServer.Account")

  cur = iacc.GetBalance()
  MsgBox "Current balance is " &amp; cur

  iacc.GetLastTransaction dte, cur
  MsgBox "Last transaction was at " &amp; dte &amp; _
    " for $" &amp; cur
End Sub</pre>
<p>Notice that there is no compile-time link between the client code above and the server object. In fact, the client project does not have to reference the AccountServer type library at all. We still reap all of the benefits of early-binding when we call GetBalance and GetLastTransaction -- primarily speed and type safety, but let's not forget the auto-complete feature -- because we have the compile-time definition of the IAccount interface in the AccountLib type library.</p>
<p>Had we used the New keyword instead of the CreateObject() function, we would have had a compile-time link between client and server. It is far easier to manage the development of a multi-project application without these dependencies. True, using New is slightly faster because it ducks one Registry lookup, but unless you really need that last ounce of performance, CreateObject() will make your life that much easier. As always, don't optimize until you have to.</p>
<p>An obvious extension of this principle would be to collect all of the application's interface declarations into a single type library during the development phase. All of the projects need only reference that one type library, eliminating the dependency issues -- especially circular references -- that can drive a development team leader to an early grave.</p>
<p>Our Account server might one day need methods to manage the account holder information: name, address, hat size, etc. In the old VB world, we would have simply added this functionality as public methods on the Account class, and adjusted the compatibility setting accordingly. In our new and improved IDL world, we're far more likely to add another interface, perhaps called IAccountInfo, to expose this functionality. To reiterate the point I made earlier about VB's single interface per class outlook: why should we group together methods that manipulate account balances with methods that perform administrative tasks for the account holder? Splitting these separate responsibilities into separate interfaces is a technique known as interface factoring, and is one of the hallmarks of interface-based programming. VB can implement as many interfaces as you can throw at it, and there's no reason why you should stick with its default interface (secretly named <em>_ClassName</em>) if you don't have to.</p>
<p>You may agree with my argument for multiple interfaces, but wonder why go to the length of using IDL when you can define COM interfaces in VB itself through abstract classes (Sub, Function, and Property declarations without any code in the method body). There are four main reasons why IDL is the preferred path:</p>
<ul>
<li>by using abstract classes, you're still allowing VB to control the interface GUIDs;</li>
<li>all such interfaces will be dual, and you remember what <em>Effective COM</em> had to say about that;</li>
<li>VB will create a coclass in the type library that you don't need and will only clog the Registry with obsolete CLSIDs as you fiddle with the method declarations in your abstract class; and</li>
<li>you're stuck with VB's interface/class naming convention which prefixes everything with an underscore. Admittedly, this is a minor problem, but annoying nonetheless.</li>
</ul>
<p>Your next logical choice would be to use VB to create the method definitions in the language that you're most familiar with, open up the type library that VB stores in the DLL or EXE using the OLE/COM Object Viewer utility, and cut &amp; paste the IDL it displays into a new IDL file. This procedure works well and is a good way to learn IDL by examining what VB-conceived interfaces look like under the covers. Ultimately though, you'll tire of this "clipboard development" and in any case you want to be in the position where you can write IDL from scratch. You'll find that IDL is a very expressive language, and should you ever choose to create an interface declaration for a language like C++ that is not bound to the OLE Automation data types, you'll quickly learn to appreciate the level of control over parameter marshalling that IDL can handle. As I like to say, "if COM is love, then IDL is flowers and chocolates."</p>
<p>But if you're still unconvinced -- and any seasoned developer has a healthy dose of skepticism -- I urge to read the very first chapter in <em>Essential COM</em>: "Define your interfaces before you define your classes (and do it in IDL)."</p>
<h3>The New Rules</h3>
<p>In the past, Visual Basic generated -- and regenerated -- the type library, interface, and coclass GUIDs on your behalf. While a convenience, this is the source of our troubles. By using IDL to define our GUIDs, we have taken on the responsibility of ensuring that the COM Standard regulations are followed precisely. You'll need two tools to assist you in this task: a source control system, and an unambiguous definition of what it means for your development team to "publish" an interface.</p>
<p>The necessity of a source control system, such as Visual SourceSafe, needs no explanation. The concept of publishing an interface, however, is not likely as familiar. When writing IDL for VB, we can specify the GUIDs for both interfaces and type libraries. These GUIDs are commonly called IIDs and LIBIDs, respectively. VB will continue to manage the coclass GUID, or CLSID, because the coclass is linked to the implementation of a component, and that implementation is written in VB.</p>
<p>It should come as no surprise that, using the Interface Definition Language, we are really talking about interfaces. True, we can also define structures and enumerated sets in IDL, but it's the interface that's of greater interest. Now, you may have read somewhere that COM interfaces are immutable. In other words, interfaces cannot be versioned: you define your interface, assign it an IID, and thus it remains until the stars burn out. All true, but the full statement should read: COM interfaces are immutable <em>once published</em>. Therefore, until such a time that you define as "published," you are completely free to add, change, or remove methods from an interface, or mess about with any of the methods' signatures. The obvious definition of "published" is the code-freeze milestone before you release your gold version to manufacturing, or to the client for installation. However, you must also consider any other team in your organization that is dependent upon your components and their interfaces. Delivering code to these groups, even if it's in the pre-alpha state, is also deemed publishing. In general, any time you distribute code or binaries to other groups that do not make changes to your source, you have "published." Clearly, you'll need a crisp definition of this point in time so that you'll know when to lock down an interface.</p>
<p>You must remember to recompile any dependent modules after you've made a change to an unpublished interface. Doing so will prevent mysterious and lethal problems, particularly if you've removed preexisting methods, or made changes to their signature.</p>
<p>Of course, during the lifecycle of any software application, it's more than likely that changes will have to be made to your component. Once published, you cannot change an interface; end of story. Instead, the COM convention is to add an interface that exposes the newly desired functionality. For example, if we needed to add a new method called CalculateInterest(), we wouldn't change the existing IAccount interface, but we would add a new interface to the type library containing our new method, perhaps called IAccount2. Although it sometimes seems a little clunky to number interfaces in this way, it's quite common. Witness the DirectX interfaces: up to IDirectDraw4, and counting.</p>
<p>If you do add new interfaces to an existing type library, you will need to increment either the library's minor or major version number, or both. Unlike interfaces, libraries can be versioned, so you will not need to change the library's GUID. Type libraries are really a convenience for gathering together type information, so their versioning rules are far more relaxed.</p>
<p>Remember too that during the development phase you are at liberty to gather together all of your application's type information into one type library, greatly simplifying inter-project dependencies. Provided you use the CreateObject() function instead of the New keyword, you'll also be able to sidestep any dependencies on the CLSID that VB still controls. You will still need New for internal VB objects such as Collections and Forms, but that's about it.</p>
<h3>Other IDL Considerations</h3>
<p>IDL is a language in its own right. Unlike the other programming languages we're familiar with, it doesn't contain any procedural statements; there are no while loops in IDL. IDL's chief task is to specify the precise syntax of interfaces. As a side effect, it also spells out the assumptions that COM can make when marshalling data and interface pointers between client and server. However, interface definitions in IDL also hint at the semantics behind the interface methods. These semantics, although not formally stipulated by IDL, are also subject to the rules of interface immutability. Just imagine if you defined an interface method called Add() that at some point later you changed to actually multiply its two arguments. Perhaps you haven't broken the letter of COM law, but certainly its spirit.</p>
<p>As a language, IDL has its own data types. For the most part, these are exactly those of the C language, of which IDL is a clear descendant. There are also a few defined data types corresponding to those used in Win32 programming. When translating from Visual Basic, use the data types in figure 2 to map to IDL.</p>
<table>
<tr>
<th>Visual Basic Data Type</th>
<th>IDL Data Type</th>
</tr>
<tr>
<td>Boolean</td>
<td>VARIANT_BOOL</td>
</tr>
<tr>
<td>Byte</td>
<td>unsigned char</td>
</tr>
<tr>
<td>Collection</td>
<td>_Collection*</td>
</tr>
<tr>
<td>Currency</td>
<td>CURRENCY</td>
</tr>
<tr>
<td>Date</td>
<td>DATE</td>
</tr>
<tr>
<td>Double</td>
<td>double</td>
</tr>
<tr>
<td>Integer</td>
<td>short</td>
</tr>
<tr>
<td>Long</td>
<td>long</td>
</tr>
<tr>
<td>Object</td>
<td>IDispatch*</td>
</tr>
<tr>
<td>Recordset</td>
<td>_Recordset*</td>
</tr>
<tr>
<td>Single</td>
<td>float</td>
</tr>
<tr>
<td>String</td>
<td>BSTR</td>
</tr>
<tr>
<td>Variant</td>
<td>VARIANT</td>
</tr>
<tr>
<td>no parameters</td>
<td>void</td>
</tr>
</table>
<p>Figure 2: Visual Basic data types and their corresponding data types in IDL</p>
<p>Other than unsigned char (Byte), keep in mind that VB can only implement signed types. Parameters marked as [in] use the IDL representation as in figure 1. These correspond to ByVal parameters in VB. Parameters marked as [in, out] add a single indirection operator (*). These correspond to VB's ByRef parameters. For example:</p>
<pre>HRESULT Method1(
  // ByVal As Integer
  [in] short intInParm,
  // ByVal As Object
  [in] IDispatch* objInParm,
  // ByRef As Integer
  [in, out] short* intInOutParm,
  // ByRef As Object
  [in, out] IDispatch** objInOutParm
);</pre>
<p>A return value for a function must be the last formal parameter in the IDL method declaration and it is specified using the [out, retval] attributes. While you do not strictly need to name these parameters, you might as well. Otherwise, the MIDL compiler will create its own fanciful and underscore-laden name. Since these parameters are [out] parameters, they also require the single indirection operator (*):</p>
<pre>HRESULT Function1(
  // ByVal As Date
  [in] DATE dteInParm,
  // Function1() As String
  [out, retval] BSTR* strOutParm
);</pre>
<p>If you want to use externally-defined types such as _Collection* or _Recordset* as parameters in your methods, you will need to import the appropriate type libraries into your library declaration. For the _Collection interface (yes, it is an interface and not a class) the type library is embedded as a resource in VB's runtime: MSVBVM60.DLL. For the ADO _Recordset interface, the appropriate type library -- even for ADO version 2.1 -- is buried within MSADO15.DLL. As an aside, don't forget the leading underscore for the _Recordset interface. Without that underscore, you're defining a parameter of type coclass Recordset, which is most certainly not what you want.</p>
<p>You can only import these type libraries using the importlib() statement within a library declaration in IDL. Should you want to declare your interfaces outside of the library block you will need the actual IDL for the _Recordset or _Collection interfaces. Fortunately, in the case of _Recordset, Martin Gudgin of DevelopMentor has already reverse-engineered the IDL for ADO 2.5 and you can download it from his site at (<a href="http://www.develop.com/marting/com/download/msado25.idl">www.develop.com/marting/com/download/msado25.idl</a>). For the _Collection interface and others, you'll have to do the job yourself using the OLE/COM Object Viewer tool.</p>
<p>As an aside, defining interfaces outside of a library declaration, in fact in separate files, is a good strategy for reuse. Like components, good interfaces can also be reused. By declaring them in distinct files, they're easier to recombine into type libraries as appropriate for the task at hand.</p>
<p>Another common element of a type library is an enumerated set of constants. It's particularly valuable to define parameters of these types because the list of constants will appear as part of the auto-complete feature whenever you're writing code to call the particular method. Each enumerated set must also have its own GUID. This may explain to some why simply changing a constant violates binary compatibility. As in the case for interfaces, you will have to freeze the set of constants once they are published. When declaring these constants in IDL, there's a sneaky trick that will ensure that the proper name for the enumerated set shows up in the Object Browser:</p>
<pre>[uuid(357265C1-4EA3-11d3-B288-00C04F534C97)]
typedef enum Constants {
  Blue = -1,
  Red = 0,
  VanDykeBrown = 54321
} Constants;</pre>
<p>If you didn't spot it, the trick is to name the enum type exactly the same as the typedef: in this example, "Constants". Otherwise the MIDL compiler will invent its own, quite unnecessary, intermediate mangled name that will show up in the Object Browser.</p>
<p>One last topic that deserves attention is the issue of DISPIDs. A DISPID is really nothing more than a number assigned to an interface method. These are of particular use for dual interfaces and dispinterfaces. They are not necessary for VTable, or IUnknown-derived, interfaces. If you omit the DISPIDs, assigned using the [id()] attribute in IDL, MIDL will assign them on your behalf.</p>
<p>DISPIDs are 32-bit integers, but only the least significant 16 bits are of interest in most cases. Visual Basic, when it generates its own type libraries sets the high bits of dual interfaces according to the following rule: hex 6003 for method declarations, and hex 6803 for property declarations. Curiously, for pure dispinterfaces, VB leaves the high bits set to zero. The particularly studious will find the complete format and rules for DISPIDs in the MSDN documentation by searching for MEMBERID in the API Reference section.</p>
<p>For properties specified using the [propget] (Property Get), [propput] (Property Let), or [propputref] (Property Set) attributes, the DISPID should be the same for all accessor (Get) and mutator (Let/Set) methods of a single logical property.</p>
<p>To assign a property as the default for the interface, use the special constant, DISPID_VALUE (equals 0). If you implement a collection class using the age-old "House of Bricks" technique, you'll need to define the NewEnum method using DISPID_NEWENUM (equals -4).</p>
<h3>The Pitfalls</h3>
<p>The combination of VB and COM suffers from its share of shortcomings, and the technique of using IDL to define interfaces adds its own. Ironically, the worst offenders affect script clients, typically the least dependent upon rigid GUID declarations. This section lists some of the most heinous examples that have plagued our development teams over the past year.</p>
<p>Although not a problem due to IDL, Visual Basic as a whole can only implement interfaces that are OLE Automation-compatible. The technical reasons for this limitation are evident, but it's an important distinction when comparing to C++. We can only hope that COM+ will deliver on its promise to narrow the language gap.</p>
<p>Related to this problem is the fact that VB cannot implement an interface that does not inherit directly from either IUnknown or IDispatch. Interface inheritance is almost as powerful a concept as traditional OO implementation inheritance. I suspect that this problem stems from the fact that the type library format does not contain detailed inheritance path information and so there is a difficulty in determining the size of the VTable for interfaces that are more than one step removed from IUnknown or IDispatch. Regrettably, many useful interfaces that we'd like to implement in VB are either not OLE Automation-compatible, or are not direct descendants from IUnknown or IDispatch. As of version 6, VB now implements at least one such interface, IPersistStreamInit, underneath the Persistable class property.</p>
<p>A severe problem directly related to the use of IDL is that VB will not implement an IDL-defined default interface. This means that scripting languages can only use the VB-generated default dual interface: _ClassName. An admittedly clumsy way to work around this limitation is to include a method in the class's default interface that returns a reference to the other IDL-defined interfaces that the class implements. As I rather cryptically mentioned earlier, this will only work for intra-apartment calls. As luck would have it, we have developed a component called the DispAdapter that solves this problem and you can download it for free from <a href="http://whathesaid.ca/2006/07/05/dispadapter-lives/">whathesaid.ca</a>. If any of the VB design team is listening, what we really need is a new syntax for the Implements statement, along the lines of:</p>
<pre>Implements [Default] ISomeInterface</pre>
<p>In a similar vein, VB cannot implement an IDL-defined source interface. This means that you cannot use IDL to define connection point events that your VB class can raise. VB will itself generate a default source dispinterface for any public events that your class defines, and it will name this dispinterface with two leading underscore characters: __ClassName. It also means that you can't treat components that respond to event interfaces in polymorphic fashion. Unless you require that script clients receive your server's events, use references to custom callback interfaces to enable bi-directional communication instead of connection point events. By doing so you can also dodge the highly inefficient construction and destruction of a connection point session. Again, we'd like to see an extended syntax for the Implements statement:</p>
<pre>Implements [Source] ISomeEventInterface</pre>
<p>We'd also need a new form of the WithEvents clause to allow us to choose which interface, or interfaces, will receive the callback when an event is raised.</p>
<p>Surprisingly, VB cannot implement an interface containing a method with a parameter of type IUnknown* or IUnknown**. Even more astonishing is that VB can create parameters of this type itself without problem. This means that you can only pass "unknown" interface references that inherit from IDispatch, or by using the VT_UNKNOWN Variant type. Neither option is particularly elegant and can be problematic when making calls across apartment boundaries. Microsoft tells us that this behaviour is by design but I believe they simply didn't anticipate anyone pushing VB's COM boundaries to this extent. Ideally, we'd use the [iid_is()] attribute to deal with runtime interface identification, but the [iid_is()] attribute does not survive the translation from IDL to the type library. Sigh.</p>
<p>Visual Basic does not support pure [out] parameters. The same functionality can be duplicated with the legal [in, out] parameters, but these can be rather exorbitant when making remote calls since the data must be marshalled in both directions rather than just one. The more subtle dilemma is that the COM specification cannot deterministically state what should happen to an [in, out] parameter during an error condition. There are some guidelines, but each case must be treated individually and depending upon the author of the server component, the results will be "undefined" -- a term guaranteed to inspire unease in the veteran developer.</p>
<p>As of Windows NT service pack 4, it is possible to specify parameters that are user-defined types (UDTs), or structs in IDL. In many cases, UDTs are preferable to other structured data representations such as variant arrays or recordsets, and offer unquestionably greater type-safety. Apparently MTS hasn't caught up though, and it will reject efforts to register a component with such an IDL-defined interface.</p>
<p>A mere annoyance, and one soon conquered, is that the VB Object Browser does not indicate which parameters in a method are [in] and which are [in, out]. If you are implementing the interfaces in your class by hand, you must correctly use ByVal and ByRef to match these two attribute combinations or VB will complain with a "procedure declaration does not match" error. Fortunately the object and procedures dropdown listboxes at the top of the code window will properly fill out the entire method signature for you.</p>
<p>Last, and pretty much least, VB cannot implement a dispinterface that contains declared properties. You must instead declare each property in the methods section using the [propget], [propput], or [propputref] attributes.</p>
<h3>Conclusion</h3>
<p>I didn't really want to end this article with such a long shopping list of faults and inadequacies. Nevertheless, these are the problems that we've encountered and I'd be less than honest if I were to sweep them under the rug. Hopefully, you'll believe that I've been equally sincere in my endorsement of the benefits this technique.</p>
<p>In the time since I began to promote using IDL to define interfaces for VB, I have been met with considerable reluctance: "It just seems so un-VB-ish." "Isn't there some tool from Sheridan or Desaware that solves this?"</p>
<p>There is a tool. It's from Microsoft, and it's called MIDL.</p>
<p>Ultimately, developers have to experience the pain of run-time error 429, of fractured project dependencies, and of endless bouts of Registry pruning before they can grasp the message. Fortunately, once converted, their appreciation of the technique has been wholehearted.</p>
<p>Visual Basic is an excellent tool for writing COM applications. The interface is the fundamental concept underlying COM. IDL is the language of interfaces. How else but through IDL could one attempt to write serious COM applications in Visual Basic?</p>
<h3>Bibliography</h3>
<p>PRB: <em>Visual Basic Does Not Understand IUnknown** Type</em>. Microsoft Corporation. Article ID: Q194913.</p>
<p>Box, Don, Keith Brown, Tim Ewald, and Chris Sells. <em>Effective COM</em>. Addison Wesley.</p>
<p>Box, Don. <em>Essential COM</em>. Addison Wesley.</p>
<p>Cleverley, James. <em>VB Programmers are COM Programmers</em>. COMdeveloper.</p>
<p>Hludzinski, Bill. <em>Understanding Interface Definition Language: A Developer's Survival Guide</em>. Microsoft Systems Journal. August 1998.</p>
<p>Johns, Paul. <em>From Typelib to Visual J++ 6.0 COM Object</em>. Microsoft Corporation.</p>
<p>Pattison, Ted. <em>Programming Distributed Applications with COM and Microsoft Visual Basic 6.0</em>. Microsoft Press.</p>
<p>Pattison, Ted, and Brian A. Randell. <em>Visual Basic Design Time Techniques to Prevent Runtime Version Conflicts</em>. Microsoft Systems Journal. January 2000.</p>
<p>Salme, Ivo. <em>Building, Versioning, and Maintaining Visual Basic Components</em>. Microsoft Corporation.</p>
<p style="text-align: left"><a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license"><img src="https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png" title="Attribution-NonCommercial-ShareAlike 4.0 International" alt="Creative Commons" style="float: left;margin-right: 15px" /></a>© 1999 Dave Rogers.<br />
Licensed under the <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Licence</a>.</p>
